from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database

router = APIRouter(tags=["Ingredients"])


@router.post("/ingredients", response_model=schemas.IngredientBase)
def create_ingredient(ingredient: schemas.IngredientBase, db: Session = Depends(database.get_db)):
    existing = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    new_ingredient = models.Ingredient(name=ingredient.name)
    db.add(new_ingredient)
    db.commit()
    db.refresh(new_ingredient)
    return new_ingredient


@router.get("/ingredients/{id}", response_model=schemas.IngredientBase)
def get_ingredient(id: int, db: Session = Depends(database.get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.put("/ingredients/{id}", response_model=schemas.IngredientBase)
def update_ingredient(id: int, updated: schemas.IngredientBase, db: Session = Depends(database.get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    ingredient.name = updated.name
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/ingredients/{id}")
def delete_ingredient(id: int, db: Session = Depends(database.get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(ingredient)
    db.commit()
    return {"message": "Ingredient deleted successfully"}


@router.get("/ingredients", response_model=List[schemas.IngredientBase])
def list_ingredients(db: Session = Depends(database.get_db)):
    return db.query(models.Ingredient).all()


@router.get("/test_db", tags=["Ingredients"])
def test_db(db: Session = Depends(database.get_db)):
    ingredients = db.query(models.Ingredient).all()
    if not ingredients:
        raise HTTPException(status_code=404, detail="No ingredients found")
    return ingredients