from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database import Base, engine

Base = declarative_base()

class MoodLog(Base):
    __tablename__ = "mood_logs"
    id = Column(Integer, primary_key=True, index=True)
    mood = Column(String)
    playlist_name = Column(String)
    playlist_url = Column(String)

Base.metadata.create_all(bind=engine)