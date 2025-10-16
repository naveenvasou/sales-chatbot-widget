from sqlalchemy.orm import Session
from app.models.lead import Lead, ChatMessage, ChatSession
from datetime import datetime
import uuid
import json
from typing import Any

class DatabaseService:
    
    @staticmethod
    def create_session(db: Session, user_ip: str = None, user_agent: str = None) -> str:
        """Create a new chat session and return session_id"""
        session_id = str(uuid.uuid4())
        
        chat_session = ChatSession(
            session_id=session_id,
            user_ip=user_ip,
            user_agent=user_agent
        )
        db.add(chat_session)
        db.commit()
        
        return session_id
    
    @staticmethod
    def save_message(db: Session, session_id: str, role: str, message: str, intent: str = None):
        """Save a chat message"""
        chat_message = ChatMessage(
            session_id=session_id,
            role=role,
            message=message,
            intent=intent
        )
        db.add(chat_message)
        
        # Update session message count
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            session.message_count += 1
        
        db.commit()
    
    @staticmethod
    def get_conversation_history(db: Session, session_id: str, limit: int = 20) -> list:
        """Get conversation history for a session"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        return list(reversed(messages))
    
    @staticmethod
    def create_or_update_lead(db: Session, session_id: str, lead_data: dict) -> Lead:
        """Create or update a lead"""
        lead = db.query(Lead).filter(Lead.session_id == session_id).first()
        
        if lead:
            # Update existing lead
            for key, value in lead_data.items():
                if value is not None:
                    setattr(lead, key, value)
            lead.updated_at = datetime.utcnow()
        else:
            # Create new lead
            lead = Lead(session_id=session_id, **lead_data)
            db.add(lead)
        
        db.commit()
        db.refresh(lead)
        
        # Mark session as lead captured
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            session.lead_captured = True
            db.commit()
        
        return lead
    
    @staticmethod
    def get_lead_by_session(db: Session, session_id: str) -> Lead:
        """Get lead by session_id"""
        return db.query(Lead).filter(Lead.session_id == session_id).first()
    
    @staticmethod
    def get_all_leads(db: Session, skip: int = 0, limit: int = 100):
        """Get all leads (for admin dashboard)"""
        return db.query(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def end_session(db: Session, session_id: str):
        """Mark a session as ended"""
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            session.is_active = False
            session.ended_at = datetime.utcnow()
            db.commit()
            
    @staticmethod
    def update_session_context(db: Session, session_id: str, context_key: str, context_value: Any):
        """Update session context data"""
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            # Parse existing context
            context = {}
            if session.context_data:
                try:
                    context = json.loads(session.context_data)
                except:
                    context = {}
            
            # Update context
            context[context_key] = context_value
            session.context_data = json.dumps(context)
            db.commit()

    @staticmethod
    def get_session_context(db: Session, session_id: str, context_key: str = None):
        """Get session context data"""
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session or not session.context_data:
            return None
        
        try:
            context = json.loads(session.context_data)
            if context_key:
                return context.get(context_key)
            return context
        except:
            return None

# Create singleton instance
db_service = DatabaseService()