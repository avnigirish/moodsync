from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from database import Base, engine

Base = declarative_base()

class MoodLog(Base):
    __tablename__ = "mood_logs"
    id = Column(Integer, primary_key=True, index=True)
    mood = Column(String)
    playlist_name = Column(String)
    playlist_url = Column(String)
    exercise = Column(String)

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)