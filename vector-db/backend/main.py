import os
import uuid
import random

import numpy as np

from fastapi import Depends, FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, Index, inspect
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapped_column

from pgvector.sqlalchemy import Vector

from torchvision import transforms, models
from torchvision.io import read_image, ImageReadMode
import torch

import cv2
import timm

# fastapi stuff
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="static")
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
templates = Jinja2Templates(directory="static")
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# db setup
Base = declarative_base()
EMBED_SIZE = int(os.environ["EMBED_SIZE"])

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    embedding = mapped_column(Vector(EMBED_SIZE))
DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

insp = inspect(engine)
indexes = insp.get_indexes("images") 
if not any(index["name"] == "embed_index" for index in indexes):
    index = Index('embed_index', Image.embedding,
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
    )
    index.create(engine)


# load model
model = timm.create_model('efficientnet_b0', pretrained=False)
model.classifier = torch.nn.Sequential(
  torch.nn.Linear(1280, 1024),
  torch.nn.ReLU(),
  torch.nn.Linear(1024, 15)
  )
model.load_state_dict(torch.load('model_state_dict.pth'))
# make last 2 layers identity, so we can get our embeddings
model.classifier[1] = torch.nn.Identity()
model.classifier[2] = torch.nn.Identity()
model.eval() 

# model transform

def normalize_transform():
    if True: # Normalization for pre-trained weights.
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
            )
    return normalize
IMAGE_SIZE = 224
def get_transform():
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        normalize_transform()
    ])
    return transform

transform = get_transform()

# seed db
seed = os.environ['SEED'] == 'true'
if seed:
    empty_table = False
    with SessionLocal() as db:
        count = db.query(func.count(Image.id)).scalar()
        empty_table = count == 0
    if empty_table:
        image_batch = []    
        for idx, filename in enumerate(os.listdir('images')):
            image = read_image('images/' + filename)
            image_batch.append(transform(image))
        image_batch = torch.stack(image_batch)
        with torch.no_grad():
            embeddings = model(image_batch).numpy()
        images = [Image(name=filename, path=f"images/{filename}", embedding=embeddings[idx]) for idx, filename in enumerate(os.listdir('images'))]
        with SessionLocal() as db:
            db.bulk_save_objects(images)
            db.commit()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_img_embed(image: UploadFile = File(...)):
    img_data = await image.read()
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img_transformed = transform(img)
    img_transformed = img_transformed.unsqueeze(0)
    with torch.no_grad():
        embedding = model(img_transformed)
    return embedding, img_data

@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save the uploaded image
    file_name = f"{uuid.uuid4()}.png"
    file_path = f"images/{file_name}"
    embedding, img_data = await get_img_embed(image)
    embedding = embedding.reshape((1024,)).tolist()

    with open(file_path, "wb") as buffer:
        buffer.write(img_data)

    img = Image(name=image.filename, path=file_path, embedding=embedding)
    db.add(img)
    db.commit()

    return {"success": True}


@app.post("/search-image")
async def search_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    query_embedding, _ = await get_img_embed(image)
    query_embedding = query_embedding.reshape((1024,)).tolist()
    # limit(3) returns nothing?
    # result = db.execute(select(Image).order_by(Image.embedding.cosine_distance(query_embedding)).limit(3)).all()
    # hold onto your network and ram- we are going to get the entire database
    result = db.execute(select(Image).order_by(Image.embedding.cosine_distance(query_embedding))).all()[:3]
    top_images = [{"id": img[0].id, "name": img[0].name, "path": img[0].path} for img in result]
    return JSONResponse(content={"results": top_images})

