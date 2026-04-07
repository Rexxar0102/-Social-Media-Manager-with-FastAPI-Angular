import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Post, User
from app.services import instagram as ig_service

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def publish_post(post_id: int):
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            logger.error(f"Post {post_id} not found")
            return
        
        user = db.query(User).first()
        if not user or not user.access_token:
            post.status = "failed"
            post.error_message = "No Instagram account connected"
            db.commit()
            return
        
        ig_service.instagram_service.set_access_token(user.access_token)
        
        if not user.instagram_business_id:
            post.status = "failed"
            post.error_message = "No Instagram Business account configured"
            db.commit()
            return
        
        caption = post.content or ""
        if post.hashtags:
            import json
            try:
                hashtags = json.loads(post.hashtags)
                if isinstance(hashtags, list):
                    caption += "\n\n" + " ".join(hashtags)
            except:
                caption += f"\n\n{post.hashtags}"
        
        try:
            if post.post_type == "photo" and post.media_url:
                result = ig_service.instagram_service.publish_photo(
                    user.instagram_business_id,
                    post.media_url,
                    caption
                )
                if "id" in result:
                    post.instagram_post_id = result["id"]
                    post.status = "published"
                else:
                    post.status = "failed"
                    post.error_message = str(result)
            
            elif post.post_type == "video" and post.media_url:
                result = ig_service.instagram_service.publish_video(
                    user.instagram_business_id,
                    post.media_url,
                    caption
                )
                if "id" in result:
                    post.instagram_post_id = result["id"]
                    post.status = "published"
                else:
                    post.status = "failed"
                    post.error_message = str(result)
            
            elif post.post_type == "text":
                result = ig_service.instagram_service.publish_text_post(
                    user.instagram_business_id,
                    caption
                )
                if "id" in result:
                    post.instagram_post_id = result["id"]
                    post.status = "published"
                else:
                    post.status = "failed"
                    post.error_message = str(result)
            
            else:
                post.status = "failed"
                post.error_message = "Missing media or invalid post type"
        
        except Exception as e:
            post.status = "failed"
            post.error_message = str(e)
            logger.error(f"Error publishing post {post_id}: {e}")
        
        db.commit()
    
    finally:
        db.close()

def schedule_post(post_id: int, scheduled_time: datetime):
    trigger = DateTrigger(run_date=scheduled_time)
    job_id = f"post_{post_id}"
    
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    scheduler.add_job(
        publish_post,
        trigger,
        args=[post_id],
        id=job_id,
        replace_existing=True
    )
    logger.info(f"Scheduled post {post_id} for {scheduled_time}")

def remove_scheduled_post(post_id: int):
    job_id = f"post_{post_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed scheduled job for post {post_id}")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")