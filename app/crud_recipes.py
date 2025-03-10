from sqlalchemy.orm import Session
from .models import Recipe, User
from fastapi import HTTPException


# create Recipe
def create_recipe(db: Session, title: str, instructions: str, user_id: int):
    db_recipe = Recipe(title=title, instructions=instructions, user_id=user_id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


# Get a singke Recipe
def get_recipe(db: Session, recipe_id: int):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe


# Get all Recipes by user
def get_all_recipes(db: Session, user_id: int):
    db_recipes = db.query(Recipe).filter(Recipe.user_id == user_id).all()
    if not db_recipes:
        raise HTTPException(status_code=404, detail="No recipes found for this user")
    return db_recipes


# Update recipe
def update_recipe(db: Session, recipe_id: int, title: str, instructions: str):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_recipe.title = title
    db_recipe.instructions = instructions
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


# Delete recipe
def delete_recipe(db: Session, recipe_id: int):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()