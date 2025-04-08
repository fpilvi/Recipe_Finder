from app.database import engine
from app import models

print("Starting table creation...")

models.Base.metadata.create_all(bind=engine)

print("Tables created successfully!")