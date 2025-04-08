from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database

router = APIRouter(tags=["Recipes"])

@router.get("/recipes/search", response_model=List[schemas.RecipeBase])
def search_recipes(ingredients: str, db: Session = Depends(database.get_db)):
    ingredient_names = [name.strip().lower() for name in ingredients.split(",")]
    db_ingredients = db.query(models.Ingredient).filter(models.Ingredient.name.in_(ingredient_names)).all()

    if not db_ingredients:
        raise HTTPException(status_code=404, detail="No ingredients found")

    recipes = db.query(models.Recipe).join(models.Recipe.ingredients).filter(
        models.Ingredient.id.in_([i.id for i in db_ingredients])
    ).all()

    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")

    return recipes


@router.post("/add_ingredient_to_recipe")
def add_ingredient_to_recipe(recipe_id: int, ingredient_name: str, quantity: str, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient_name).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    recipe_ingredient = models.RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity=quantity
    )

    db.add(recipe_ingredient)
    db.commit()

    return {"message": "Ingredient added to recipe successfully"}

@router.post("/recipes", response_model=schemas.RecipeBase)
def create_recipe(
    recipe: schemas.RecipeBase,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_recipe = models.Recipe(
        title=recipe.title,
        instructions=recipe.instructions,
        user_id=current_user.id
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for ingredient in recipe.ingredients:
        db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
        if not db_ingredient:
            db_ingredient = models.Ingredient(name=ingredient.name)
            db.add(db_ingredient)
            db.commit()
            db.refresh(db_ingredient)

        db_recipe_ingredient = models.RecipeIngredient(
            recipe_id=db_recipe.id,
            ingredient_id=db_ingredient.id,
            quantity=getattr(ingredient, "quantity", None),
            unit=getattr(ingredient, "unit", None)
        )
        db.add(db_recipe_ingredient)

    db.commit()
    return db_recipe


@router.get("/recipes/{id}", response_model=schemas.RecipeRead)
def get_recipe(id: int, db: Session = Depends(database.get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/recipes/{id}", response_model=schemas.RecipeRead)
def update_recipe(
    id: int,
    updated_recipe: schemas.RecipeCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

    recipe.title = updated_recipe.title
    recipe.instructions = updated_recipe.instructions
    db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe.id).delete()

    for ingredient in updated_recipe.ingredients:
        db_ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == ingredient.name).first()
        if not db_ingredient:
            db_ingredient = models.Ingredient(name=ingredient.name)
            db.add(db_ingredient)
            db.commit()
            db.refresh(db_ingredient)

        db_recipe_ingredient = models.RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=db_ingredient.id,
            quantity=ingredient.quantity,
            unit=ingredient.unit
        )
        db.add(db_recipe_ingredient)

    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/recipes/{id}")
def delete_recipe(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")

    db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe.id).delete()
    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}