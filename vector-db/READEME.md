# Reverse File Search

## Why?

The point of this project was to fine-tune efficientnet-b0 for the purpose of embeddding generation. The typical thing to do would be running PCA on these embeddings to plot them in 2d...this is boring. We can just make a search engine

## How much time did we waste?

We wasted time with the following:

- Wrote a React frontend to give our search engine a nice UI
- Wrote a FastAPI backend for our nice frontend
- Seeded db with images so anyone, anywhere (with docker) can demo it
- Battled docker. It was light. Docker is nice to use. Forgetting to change a file path is not.
- We put our embeddings into postgres with pgvector and queried with sqlalchemy, p easy to use
- threw our db setup into an init sql and dockerfile as well
- threw everything into a docker compose (we love forgetting commands, regoogling them as bash didnt remember them and reentering them as much as any oother developer)
- and probably more

## What did we learn?

a lot

## Actual takeaways
- Modern build tools like docker and vite make configuring postgres, pgvector, react, all the dependencies, static files and model very simple

## Running this yourself

Warning: this takes forever for pip to install everything (like at least 30 minutes). We could give you the image, but we want you to suffer through a build too. So, crack an egg on the hot part of your laptop and make a nice lunch while this builds.

`docker compose up --build`

Startup performance should be less than 30 seconds.

## A thanks

A thanks goes out to our Professor, Dr Fouhey. A true legend and madlad. More thanks to all the engineers before us. All of your pain allowed us to code this up in a blink of an eye.