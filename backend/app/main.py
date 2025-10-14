from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.services.gemini_service import gemini_service
from pydantic import BaseModel
from app.database import init_db, get_db
from sqlalchemy.orm import Session
from app.services.database_service import db_service
from app.api import chat
from app.api import chat_v2 
from app.services.conversation_service_v2 import conversation_service_v2


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"🚀 {settings.app_name} v{settings.app_version} started successfully!")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)  
app.include_router(chat_v2.router)

@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} API is running!",
        "version": settings.app_version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/test-gemini")
async def test_gemini():
    """Test endpoint to verify Gemini API connection"""
    result = await gemini_service.test_connection()
    return result

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat-test")
async def chat_test(request: ChatRequest):
    """Simple test endpoint for chatting with Gemini"""
    response = await gemini_service.generate_response(request.message)
    return {
        "user_message": request.message,
        "ai_response": response
    }
    
@app.get("/api/admin/leads")
async def get_all_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Admin endpoint to view all leads"""
    leads = db_service.get_all_leads(db, skip=skip, limit=limit)
    return {
        "total": len(leads),
        "leads": [
            {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "purpose": lead.purpose,
                "location": lead.location,
                "budget": lead.budget,
                "timeline": lead.timeline,
                "lead_status": lead.lead_status,
                "is_qualified": lead.is_qualified,
                "created_at": lead.created_at.isoformat()
            }
            for lead in leads
        ]
    }
    
@app.get("/api/test/greeting")
async def test_greeting():
    """Test new greeting with categories"""
    return conversation_service_v2.get_greeting()

@app.post("/api/test/validate-lead")
async def test_validate_lead(lead_data: dict):
    """Test lead validation"""
    return conversation_service_v2.validate_lead_data(lead_data)