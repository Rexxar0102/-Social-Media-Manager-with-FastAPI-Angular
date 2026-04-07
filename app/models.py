from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    access_token = Column(Text)
    page_id = Column(String(255))
    instagram_business_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_type = Column(String(50))  # video, photo, text
    content = Column(Text)
    hashtags = Column(Text)  # JSON string
    media_path = Column(String(500))
    media_url = Column(String(500))
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="draft")  # draft, scheduled, published, failed
    instagram_post_id = Column(String(255))
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)