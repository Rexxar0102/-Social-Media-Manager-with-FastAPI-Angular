from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import os
import uuid

from app.database import get_db
from app.models import Post, User
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.services.scheduler import schedule_post, remove_scheduled_post, start_scheduler

router = APIRouter()

UPLOAD_DIR = "backend/media"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/posts", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/posts/scheduled/calendar")
def get_scheduled_posts(start: Optional[str] = None, end: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Post).filter(Post.scheduled_at.isnot(None))
    
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            query = query.filter(Post.scheduled_at >= start_dt)
        except:
            pass
    
    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            query = query.filter(Post.scheduled_at <= end_dt)
        except:
            pass
    
    posts = query.all()
    
    events = []
    for post in posts:
        status_color = "#10B981" if post.status == "published" else "#F59E0B" if post.status == "scheduled" else "#6366F1"
        events.append({
            "id": post.id,
            "title": f"{post.post_type.upper()}: {post.content[:30] if post.content else 'No content'}...",
            "start": post.scheduled_at.isoformat() if post.scheduled_at else None,
            "end": post.scheduled_at.isoformat() if post.scheduled_at else None,
            "backgroundColor": status_color,
            "extendedProps": {
                "type": post.post_type,
                "status": post.status,
                "content": post.content
            }
        })
    
    return events

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_type: str = Form(...),
    content: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),
    scheduled_at: Optional[str] = Form(None),
    media_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    media_path = None
    
    if file:
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".bin"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        media_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(media_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        media_path = f"/media/{unique_filename}"
    
    scheduled_datetime = None
    if scheduled_at:
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        except:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_at)
            except:
                pass
    
    new_post = Post(
        post_type=post_type,
        content=content,
        hashtags=hashtags,
        media_path=media_path,
        media_url=media_url,
        scheduled_at=scheduled_datetime,
        status="scheduled" if scheduled_datetime else "draft"
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    if scheduled_datetime and scheduled_datetime > datetime.utcnow():
        schedule_post(new_post.id, scheduled_datetime)
    
    return new_post

@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    if "scheduled_at" in update_data and update_data["scheduled_at"]:
        new_scheduled = update_data["scheduled_at"]
        
        if new_scheduled and new_scheduled > datetime.utcnow():
            schedule_post(post_id, new_scheduled)
            post.status = "scheduled"
        elif new_scheduled:
            remove_scheduled_post(post_id)
            post.status = "draft"
    
    for key, value in update_data.items():
        setattr(post, key, value)
    
    db.commit()
    db.refresh(post)
    return post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.media_path:
        full_path = os.path.join("backend", post.media_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)
    
    remove_scheduled_post(post_id)
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

@router.post("/posts/{post_id}/publish")
def publish_now(post_id: int, db: Session = Depends(get_db)):
    from app.services.scheduler import publish_post
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    publish_post(post_id)
    
    post = db.query(Post).filter(Post.id == post_id).first()
    return {"status": post.status, "instagram_post_id": post.instagram_post_id}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Post).count()
    scheduled = db.query(Post).filter(Post.status == "scheduled").count()
    published = db.query(Post).filter(Post.status == "published").count()
    drafts = db.query(Post).filter(Post.status == "draft").count()
    failed = db.query(Post).filter(Post.status == "failed").count()
    
    return {
        "total": total,
        "scheduled": scheduled,
        "published": published,
        "drafts": drafts,
        "failed": failed
    }