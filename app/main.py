import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app import models, database
from app.auth import router as auth_router
from app.recipes import router as recipes_router
from app.ingredients import router as ingredients_router

load_dotenv()

engine = database.engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(recipes_router)
app.include_router(ingredients_router)


@app.get("/", tags=["Info"])
def read_root():
    return {"message": "Welcome to the Recipe Finder API!"}