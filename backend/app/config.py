from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Real Estate Lead Chatbot"
    app_version: str = "1.0.0"
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-lite"
    
    # Database Configuration
    database_url: str = "sqlite:///./chatbot.db"
    
    # Email Configuration (we'll use this later)
    smtp_server: str 
    smtp_port: int
    smtp_username: str 
    smtp_password: str 
    admin_email: str 
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()