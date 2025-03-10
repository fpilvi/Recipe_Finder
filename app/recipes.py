from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud_recipes, models, database
from .auth import oauth2_scheme
from fastapi import Security

router = APIRouter()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    return crud_recipe.get_user_from_token(db, token)

@router.post("/recipes/")
def create_recipe(title: str, instructions: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud_recipe.create_recipe(db, title, instructions, current_user.id)

@router.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud_recipe.get_recipe(db, recipe_id)

@router.get("/recipes/")
def get_all_recipes(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud_recipe.get_all_recipes(db, current_user.id)

@router.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, title: str, instructions: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud_recipe.update_recipe(db, recipe_id, title, instructions)

@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud_recipe.delete_recipe(db, recipe_id)