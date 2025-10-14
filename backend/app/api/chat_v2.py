from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal, Dict, Any
from app.database import get_db
from app.services.conversation_service_v2 import conversation_service_v2
from app.services.flow_manager import flow_manager
from app.services.database_service import db_service
from app.services.email_service import email_service

router = APIRouter(prefix="/api/v2", tags=["chat-v2"])


# Request/Response Models
class ChatInitRequest(BaseModel):
    """Initialize a new chat session"""
    pass


class CategorySelectRequest(BaseModel):
    """User selects a category"""
    session_id: str
    category: Literal["brochure", "booking", "availability", "question", "other"]


class LeadCaptureRequest(BaseModel):
    """User submits lead information"""
    session_id: str
    category: str
    name: str
    email: EmailStr
    phone: str


class UserInputRequest(BaseModel):
    """User provides input (button click, form submission, text)"""
    session_id: str
    input_type: str  # "button", "form", "text"
    input_data: Any  # Button value, form data dict, or text string
    current_state: str


class MenuRequest(BaseModel):
    """User requests to go back to main menu"""
    session_id: str


class ChatResponse(BaseModel):
    """Standard chat response"""
    session_id: str
    message: str
    current_state: str
    next_state: Optional[str]
    ui_component: Optional[Dict[str, Any]]
    show_menu_button: bool
    metadata: Optional[Dict[str, Any]] = None


# ==================== ENDPOINTS ====================

@router.post("/chat/init", response_model=ChatResponse)
async def initialize_chat(
    request: ChatInitRequest,
    db: Session = Depends(get_db)
):
    """
    Initialize a new chat session and return greeting with categories
    """
    try:
        # Create new session
        session_id = db_service.create_session(db)
        
        # Get greeting with categories
        greeting = conversation_service_v2.get_greeting()
        
        # Save greeting message
        db_service.save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            message=greeting["message"],
            intent="GREETING"
        )
        
        return ChatResponse(
            session_id=session_id,
            message=greeting["message"],
            current_state="greeting",
            next_state="category_selection",
            ui_component={
                "type": "category_buttons",
                "data": {
                    "categories": greeting["categories"]
                }
            },
            show_menu_button=False
        )
        
    except Exception as e:
        print(f"Error initializing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/select-category", response_model=ChatResponse)
async def select_category(
    request: CategorySelectRequest,
    db: Session = Depends(get_db)
):
    """
    User selects a category, return lead capture form
    """
    try:
        # Save user's category selection
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="user",
            message=f"Selected category: {request.category}",
            intent="CATEGORY_SELECTION"
        )
        
        # Update lead with selected category
        db_service.create_or_update_lead(
            db=db,
            session_id=request.session_id,
            lead_data={"selected_category": request.category}
        )
        
        # Get lead capture form
        form_response = conversation_service_v2.get_lead_capture_form(request.category)
        
        # Save bot's form request
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="assistant",
            message=form_response["message"],
            intent="LEAD_CAPTURE"
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=form_response["message"],
            current_state="lead_capture",
            next_state="lead_submitted",
            ui_component={
                "type": "lead_form",
                "data": {
                    "fields": form_response["form_fields"]
                }
            },
            show_menu_button=True
        )
        
    except Exception as e:
        print(f"Error in category selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/submit-lead", response_model=ChatResponse)
async def submit_lead(
    request: LeadCaptureRequest,
    db: Session = Depends(get_db)
):
    """
    User submits lead information, validate and start category flow
    """
    try:
        # Validate lead data
        validation = conversation_service_v2.validate_lead_data({
            "name": request.name,
            "email": request.email,
            "phone": request.phone
        })
        
        if not validation["valid"]:
            return ChatResponse(
                session_id=request.session_id,
                message=" ".join(validation["errors"]),
                current_state="lead_capture",
                next_state="lead_capture",
                ui_component={
                    "type": "lead_form",
                    "data": {
                        "fields": conversation_service_v2.get_lead_capture_form(request.category)["form_fields"],
                        "errors": validation["errors"]
                    }
                },
                show_menu_button=True
            )
        
        # Save lead information
        cleaned_data = validation["cleaned_data"]
        lead = db_service.create_or_update_lead(
            db=db,
            session_id=request.session_id,
            lead_data={
                "name": cleaned_data["name"],
                "email": cleaned_data["email"],
                "phone": cleaned_data["phone"],
                "selected_category": request.category,
                "is_qualified": True
            }
        )
        
        # Save user's form submission as message
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="user",
            message=f"Submitted: {cleaned_data['name']}, {cleaned_data['email']}, {cleaned_data['phone']}",
            intent="LEAD_SUBMITTED"
        )
        
        # Send email notification (lead captured!)
        await email_service.send_lead_notification(
            lead_data={
                "name": cleaned_data["name"],
                "email": cleaned_data["email"],
                "phone": cleaned_data["phone"],
                "purpose": request.category,
                "selected_category": request.category
            },
            session_id=request.session_id
        )
        
        # Start category-specific flow using state machine
        flow_response = flow_manager.start_category_flow(
            category=request.category,
            lead_data=cleaned_data
        )
        
        # Save assistant's response
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="assistant",
            message=flow_response["message"],
            intent=flow_response["current_state"]
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=flow_response["message"],
            current_state=flow_response["current_state"],
            next_state=flow_response["next_state"],
            ui_component=flow_response["ui_component"],
            show_menu_button=flow_response["show_menu_button"],
            metadata={"lead_captured": True}
        )
        
    except Exception as e:
        print(f"Error submitting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/input", response_model=ChatResponse)
async def handle_user_input(
    request: UserInputRequest,
    db: Session = Depends(get_db)
):
    """
    Handle user input during flow (button clicks, form submissions, text)
    """
    try:
        # Get lead data for context
        lead = db_service.get_lead_by_session(db, request.session_id)
        if not lead or not lead.name:
            raise HTTPException(
                status_code=400,
                detail="Lead information not found. Please start over."
            )
        
        context = {
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone
        }
        
        # Save user input
        user_message = _format_user_input(request.input_type, request.input_data)
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="user",
            message=user_message,
            intent=request.current_state
        )
        
        # Process input through flow manager
        flow_response = flow_manager.handle_user_input(
            current_state=request.current_state,
            user_input=request.input_data,
            context=context
        )
        
        # Update lead with any new data collected
        if flow_response.get("user_data"):
            _update_lead_from_flow_data(
                db=db,
                session_id=request.session_id,
                flow_data=flow_response["user_data"]
            )
        
        # Save assistant response
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="assistant",
            message=flow_response["message"],
            intent=flow_response["current_state"]
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=flow_response["message"],
            current_state=flow_response["current_state"],
            next_state=flow_response["next_state"],
            ui_component=flow_response["ui_component"],
            show_menu_button=flow_response["show_menu_button"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error handling user input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/menu", response_model=ChatResponse)
async def back_to_menu(
    request: MenuRequest,
    db: Session = Depends(get_db)
):
    """
    User requests to go back to main menu
    """
    try:
        # Save user action
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="user",
            message="Back to main menu",
            intent="MENU_REQUEST"
        )
        
        # Get menu response
        menu_response = flow_manager.go_to_main_menu()
        
        # Save assistant response
        db_service.save_message(
            db=db,
            session_id=request.session_id,
            role="assistant",
            message=menu_response["message"],
            intent="MENU"
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=menu_response["message"],
            current_state=menu_response["current_state"],
            next_state=menu_response["next_state"],
            ui_component=menu_response["ui_component"],
            show_menu_button=False
        )
        
    except Exception as e:
        print(f"Error returning to menu: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/end")
async def end_chat(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    End the chat session
    """
    try:
        lead = db_service.get_lead_by_session(db, session_id)
        
        handoff_message = f"Thank you for chatting with us, {lead.name if lead else 'there'}! Our team will be in touch soon. Have a great day! 🙏✨"
        
        # Save handoff message
        db_service.save_message(
            db=db,
            session_id=session_id,
            role="assistant",
            message=handoff_message,
            intent="HANDOFF"
        )
        
        # Mark session as ended
        db_service.end_session(db, session_id)
        
        return {
            "message": handoff_message,
            "session_ended": True
        }
        
    except Exception as e:
        print(f"Error ending chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HELPER METHODS ====================

def _format_user_input(input_type: str, input_data: Any) -> str:
    """Format user input for saving to database"""
    if input_type == "button":
        return f"Selected: {input_data}"
    elif input_type == "form":
        if isinstance(input_data, dict):
            items = [f"{k}: {v}" for k, v in input_data.items()]
            return f"Submitted form: {', '.join(items)}"
        return str(input_data)
    elif input_type == "text":
        return str(input_data)
    return str(input_data)


def _update_lead_from_flow_data(db: Session, session_id: str, flow_data: Dict[str, Any]):
    """Update lead with data collected during flow"""
    # Map flow data to lead fields
    lead_update = {}
    
    # Budget mapping
    if "budget" in flow_data:
        lead_update["budget"] = flow_data["budget"]
    
    # Location mapping
    if "location" in flow_data:
        if isinstance(flow_data["location"], list):
            lead_update["location"] = ", ".join(flow_data["location"])
        else:
            lead_update["location"] = flow_data["location"]
    
    # Property type mapping
    if "property_type" in flow_data:
        lead_update["property_type"] = flow_data["property_type"]
    
    # Timeline mapping
    if "timeline" in flow_data:
        lead_update["timeline"] = flow_data["timeline"]
    
    # Notes - append any additional info
    notes_items = []
    for key, value in flow_data.items():
        if key not in ["budget", "location", "property_type", "timeline", "name", "email", "phone"]:
            notes_items.append(f"{key}: {value}")
    
    if notes_items:
        existing_lead = db_service.get_lead_by_session(db, session_id)
        existing_notes = existing_lead.notes if existing_lead and existing_lead.notes else ""
        new_notes = "; ".join(notes_items)
        lead_update["notes"] = f"{existing_notes}; {new_notes}" if existing_notes else new_notes
    
    if lead_update:
        db_service.create_or_update_lead(db, session_id, lead_update)