from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    post_type: str
    content: Optional[str] = None
    hashtags: Optional[str] = None
    media_path: Optional[str] = None
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = None
    hashtags: Optional[str] = None
    media_path: Optional[str] = None
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None

class PostResponse(PostBase):
    id: int
    status: str
    instagram_post_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    access_token: str
    page_id: str
    instagram_business_id: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuthUrlResponse(BaseModel):
    auth_url: str

class SettingsResponse(BaseModel):
    connected: bool
    username: Optional[str] = None
    page_id: Optional[str] = None