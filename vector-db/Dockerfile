# Frontend build
FROM node:14 AS frontend-build

WORKDIR /app/frontend

COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend/ .

RUN npm run build

# Backend setup
FROM python:3.8

ENV DATABASE_URL=${DATABASE_URL}
ENV EMBED_SIZE=${EMBED_SIZE}

WORKDIR /app

# OpenCV needsthis
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend/ .

# seed images
COPY ./backend/images /app/images

# pretrained model

COPY ./backend/model_state_dict.pth /app/model_state_dict.pth

COPY --from=frontend-build /app/frontend/dist /app/static

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
