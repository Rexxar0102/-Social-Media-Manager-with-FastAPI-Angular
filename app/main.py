from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import engine, Base
from app.routes import posts, auth, settings
from app.services.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SocialPost Pro", description="Social Media Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/api", tags=["posts"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(settings.router, prefix="/api", tags=["settings"])

media_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "media")
if os.path.exists(media_path):
    app.mount("/media", StaticFiles(directory=media_path), name="media")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def root():
    return {"message": "SocialPost Pro API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}