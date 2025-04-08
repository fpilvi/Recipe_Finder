from pydantic import BaseModel
from typing import List, Optional


class IngredientCreate(BaseModel):
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None


class IngredientBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    instructions: str


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]


class RecipeRead(RecipeBase):
    ingredients: List[IngredientBase]

    class Config:
        from_attributes = True
