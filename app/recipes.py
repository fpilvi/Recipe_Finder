from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database

router = APIRouter(tags=["Recipes"])

@router.post("/recipes", response_model=schemas.RecipeBase)
def create_recipe(recipe: schemas.RecipeBase, db: Session = Depends(database.get_db)):
    db_recipe = models.Recipe(title=recipe.title, instructions=recipe.instructions, user_id=1)  # Replace with current user logic if needed
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.get("/recipes/{id}", response_model=schemas.RecipeBase)
def get_recipe(id: int, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/recipes/{id}", response_model=schemas.RecipeBase)
def update_recipe(id: int, updated_recipe: schemas.RecipeBase, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.title = updated_recipe.title
    recipe.instructions = updated_recipe.instructions
    db.commit()
    db.refresh(recipe)
    return recipe

@router.delete("/recipes/{id}")
def delete_recipe(id: int, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}