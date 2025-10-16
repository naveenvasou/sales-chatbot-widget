from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.conversation_service import conversation_service
from app.services.database_service import db_service
from app.services.email_service import email_service  # Add this import
from typing import Optional

router = APIRouter(prefix="/api", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    stage: str


@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """
    Main chat endpoint - handles conversation with lead qualification
    """
    
    try:
        # Get or create session
        session_id = message.session_id
        if not session_id:
            session_id = db_service.create_session(db)
        
        # Save user message
        db_service.save_message(
            db=db,
            session_id=session_id,
            role="user",
            message=message.message
        )
        
        # Get conversation history
        history = db_service.get_conversation_history(db, session_id)
        
        # Format history for Gemini
        gemini_history = [
            {
                "role": msg.role,
                "parts": [msg.message]
            }
            for msg in history[:-1]  # Exclude the message we just saved
        ]
        
        # Get existing lead data
        lead = db_service.get_lead_by_session(db, session_id)
        lead_data = {}
        if lead:
            lead_data = {
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "purpose": lead.purpose,
                "location": lead.location,
                "budget": lead.budget,
                "timeline": lead.timeline,
                "property_type": lead.property_type
            }
        
        # Generate AI response
        result = await conversation_service.generate_response(
            user_message=message.message,
            conversation_history=gemini_history,
            lead_data=lead_data
        )
        
        # Save AI response
        db_service.save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            message=result["response"],
            intent=result["stage"]
        )
        
        # Update lead data if new information was extracted
        if result["extracted_data"]:
            # Get previous lead state (before update)
            previous_lead = db_service.get_lead_by_session(db, session_id)
            had_contact_info_before = previous_lead and (previous_lead.email or previous_lead.phone)
            
            # Update the lead
            updated_lead = db_service.create_or_update_lead(
                db=db,
                session_id=session_id,
                lead_data=result["extracted_data"]
            )
            
            # Check if contact info was just captured (NEW contact info)
            has_contact_info_now = updated_lead and (updated_lead.email or updated_lead.phone)
            
            if has_contact_info_now and not had_contact_info_before:
                print(f"🎯 NEW LEAD QUALIFIED - Sending email notification")
                # This is a newly qualified lead - send notification
                lead_data_for_email = {
                    "name": updated_lead.name,
                    "email": updated_lead.email,
                    "phone": updated_lead.phone,
                    "purpose": updated_lead.purpose,
                    "location": updated_lead.location,
                    "budget": updated_lead.budget,
                    "timeline": updated_lead.timeline,
                    "property_type": updated_lead.property_type
                }
                
                email_sent = await email_service.send_lead_notification(
                    lead_data=lead_data_for_email,
                    session_id=session_id
                )
                
                if email_sent:
                    print(f"✅ EMAIL SENT FOR LEAD: {lead_data_for_email.get('name', 'Unknown')}")
                else:
                    print(f"❌ EMAIL FAILED FOR LEAD: {lead_data_for_email.get('name', 'Unknown')}")
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            stage=result["stage"]
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get conversation history for a session"""
    
    history = db_service.get_conversation_history(db, session_id)
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat(),
                "intent": msg.intent
            }
            for msg in history
        ]
    }
    
@router.post("/chat/select-category")
async def select_category(request: dict, db: Session = Depends(get_db)):
    """Handle category selection"""
    session_id = request.get("session_id")
    category = request.get("category")
    
    # Start the flow for selected category
    result = flow_manager.start_category_flow(category, {})
    
    return {
        "message": result["message"],
        "current_state": result["current_state"],
        "ui_component": result.get("ui_component"),
        "show_menu_button": result.get("show_menu_button", True)
    }