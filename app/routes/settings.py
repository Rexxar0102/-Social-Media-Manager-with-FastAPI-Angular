from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import SettingsResponse

router = APIRouter()

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
    user.username = token_data.get("username", "")
    
    db.commit()
    return {"message": "Settings saved"}

@router.post("/settings/disconnect")
def disconnect(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if user:
        db.delete(user)
        db.commit()
    return {"message": "Disconnected from Instagram"}