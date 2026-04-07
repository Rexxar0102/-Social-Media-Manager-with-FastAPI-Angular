import httpx
import json
from typing import Optional, Dict, Any

class InstagramService:
    def __init__(self, access_token: str = None):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def set_access_token(self, access_token: str):
        self.access_token = access_token
    
    def get_authorization_url(self, client_id: str, redirect_uri: str) -> str:
        scope = "instagram_basic,instagram_manage_content,pages_show_list,pages_read_engagement"
        return (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"
        )
    
    def exchange_code_for_token(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        response = httpx.get(url, params=params)
        return response.json()
    
    def get_long_lived_token(self, client_id: str, client_secret: str, short_token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "fb_exchange_token": short_token
        }
        response = httpx.get(url, params=params)
        return response.json()
    
    def get_user_pages(self) -> Dict[str, Any]:
        url = f"{self.base_url}/me/accounts"
        params = {"access_token": self.access_token}
        response = httpx.get(url, params=params)
        return response.json()
    
    def get_instagram_account(self, page_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{page_id}"
        params = {
            "fields": "instagram_business_account",
            "access_token": self.access_token
        }
        response = httpx.get(url, params=params)
        return response.json()
    
    def publish_photo(self, instagram_account_id: str, image_url: str, caption: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{instagram_account_id}/media"
        data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        response = httpx.post(url, data=data)
        return response.json()
    
    def publish_video(self, instagram_account_id: str, video_url: str, caption: str, cover_url: str = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{instagram_account_id}/media"
        data = {
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        if cover_url:
            data["cover_url"] = cover_url
        response = httpx.post(url, data=data)
        return response.json()
    
    def publish_container(self, instagram_account_id: str, caption: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{instagram_account_id}/media"
        data = {
            "caption": caption,
            "access_token": self.access_token
        }
        response = httpx.post(url, data=data)
        return response.json()
    
    def publish_text_post(self, instagram_account_id: str, caption: str) -> Dict[str, Any]:
        return self.publish_container(instagram_account_id, caption)
    
    def get_media_status(self, container_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{container_id}"
        params = {"access_token": self.access_token}
        response = httpx.get(url, params=params)
        return response.json()
    
    def publish_media_container(self, container_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{container_id}/publish"
        data = {"access_token": self.access_token}
        response = httpx.post(url, data=data)
        return response.json()

instagram_service = InstagramService()