from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from passlib.hash import bcrypt
from datetime import datetime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar_path = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    dietary_preferences = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recipes = relationship("Recipe", back_populates="user")

    def verify_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.verify(password, self.hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a plaintext password."""
        return bcrypt.hash(password)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    instructions = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="recipes")
    ingredients = relationship("Ingredient", secondary="recipe_ingredients", back_populates="recipes")


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    name = Column(String, index=True, unique=True)

    recipes = relationship("Recipe", secondary="recipe_ingredients", back_populates="ingredients")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = Column(String, nullable=True)
    unit = Column(String, nullable=True)