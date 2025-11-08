from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from app.env import user, password, db_name

DB_USER = os.getenv("DB_USER", user)
DB_PASSWORD = os.getenv("DB_PASSWORD", password)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "15432")
DB_NAME = os.getenv("DB_NAME",  db_name)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# check concnectivity

if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")
