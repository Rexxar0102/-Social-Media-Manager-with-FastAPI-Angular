from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic_settings import BaseSettings

from app.database import get_db
from app.models import User
from app.schemas import AuthUrlResponse, SettingsResponse, UserCreate
from app.services.instagram import instagram_service

router = APIRouter()

settings = BaseSettings()

@router.get("/auth/url", response_model=AuthUrlResponse)
def get_auth_url():
    if not settings.instagram_client_id:
        raise HTTPException(status_code=400, detail="Instagram Client ID not configured")
    
    auth_url = instagram_service.get_authorization_url(
        settings.instagram_client_id,
        settings.instagram_redirect_uri
    )
    return {"auth_url": auth_url}

@router.get("/auth/callback")
def auth_callback(code: str = Query(...), db: Session = Depends(get_db)):
    if not settings.instagram_client_id or not settings.instagram_client_secret:
        raise HTTPException(status_code=400, detail="Instagram credentials not configured")
    
    token_data = instagram_service.exchange_code_for_token(
        settings.instagram_client_id,
        settings.instagram_client_secret,
        code,
        settings.instagram_redirect_uri
    )
    
    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    short_token = token_data["access_token"]
    
    long_token_data = instagram_service.get_long_lived_token(
        settings.instagram_client_id,
        settings.instagram_client_secret,
        short_token
    )
    
    access_token = long_token_data.get("access_token", short_token)
    
    pages_data = instagram_service.get_user_pages()
    pages = pages_data.get("data", [])
    
    if not pages:
        raise HTTPException(status_code=400, detail="No Facebook pages found")
    
    page = pages[0]
    page_id = page["id"]
    
    ig_data = instagram_service.get_instagram_account(page_id)
    instagram_business_id = ig_data.get("instagram_business_account", {}).get("id")
    
    if not instagram_business_id:
        raise HTTPException(status_code=400, detail="No Instagram Business account found")
    
    user = db.query(User).first()
    if not user:
        user = User(
            access_token=access_token,
            page_id=page_id,
            instagram_business_id=instagram_business_id
        )
        db.add(user)
    else:
        user.access_token = access_token
        user.page_id = page_id
        user.instagram_business_id = instagram_business_id
    
    db.commit()
    
    return {"message": "Successfully connected to Instagram"}

@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if user and user.access_token:
        return {
            "connected": True,
            "username": user.username,
            "page_id": user.page_id
        }
    return {"connected": False}

@router.post("/settings/connect")
def save_tokens(token_data: dict, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        user = User()
        db.add(user)
    
    user.access_token = token_data.get("access_token", "")
    user.page_id = token_data.get("page_id", "")
    user.instagram_business_id = token_data.get("instagram_business_id", "")
    
    db.commit()
    return {"message": "Settings saved"}

@router.post("/settings/disconnect")
def disconnect(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if user:
        db.delete(user)
        db.commit()
    return {"message": "Disconnected from Instagram"}