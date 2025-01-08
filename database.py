from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)