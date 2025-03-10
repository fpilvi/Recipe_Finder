from fastapi import FastAPI
from app.database import engine, Base
from app.auth import router as auth_router
from app.recipes import router as recipes_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(recipes_router, prefix="/recipes", tags=["Recipes"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe Finder API!"}