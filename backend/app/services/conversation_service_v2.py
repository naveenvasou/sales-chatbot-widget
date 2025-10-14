from app.services.gemini_service import gemini_service
from app.prompts.system_prompts import (
    GREETING_MESSAGE,
    LEAD_CAPTURE_MESSAGE,
    CATEGORIES,
    BROCHURE_ASSISTANT_PROMPT,
    BOOKING_ASSISTANT_PROMPT,
    AVAILABILITY_ASSISTANT_PROMPT,
    FAQ_ASSISTANT_PROMPT,
    HANDOFF_MESSAGE,
    VALIDATION_MESSAGES
)
import re

class ConversationServiceV2:
    """
    New conversation service for button-driven flow with lead capture first
    """
    
    def get_greeting(self) -> dict:
        """Return initial greeting with category buttons"""
        return {
            "message": GREETING_MESSAGE,
            "type": "greeting",
            "show_categories": True,
            "categories": [
                {
                    "id": key,
                    "label": value["label"],
                    "emoji": value["emoji"]
                }
                for key, value in CATEGORIES.items()
            ]
        }
        
    def get_lead_capture_form(self, category: str) -> dict:
        """Return lead capture form request"""
        return {
            "message": LEAD_CAPTURE_MESSAGE,
            "type": "lead_capture",
            "category": category,
            "show_form": True,
            "form_fields": [
                {"name": "name", "label": "Full Name", "type": "text", "required": True},
                {"name": "email", "label": "Email Address", "type": "email", "required": True},
                {"name": "phone", "label": "Phone / WhatsApp", "type": "tel", "required": True}
            ]
        }
        
    def validate_lead_data(self, lead_data: dict) -> dict:
        """Validate lead capture data"""
        errors = []
        
        # Validate name
        name = lead_data.get("name", "").strip()
        if not name or len(name) < 2:
            errors.append(VALIDATION_MESSAGES["invalid_name"])
        
        # Validate email
        email = lead_data.get("email", "").strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_pattern, email):
            errors.append(VALIDATION_MESSAGES["invalid_email"])
        
        # Validate phone
        phone = lead_data.get("phone", "").strip()
        phone_clean = re.sub(r'[^0-9]', '', phone)
        if not phone_clean or len(phone_clean) != 10:
            errors.append(VALIDATION_MESSAGES["invalid_phone"])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "cleaned_data": {
                "name": name,
                "email": email.lower(),
                "phone": phone_clean
            } if len(errors) == 0 else None
        }
        
    async def handle_category_interaction(
        self,
        category: str,
        user_message: str,
        lead_data: dict,
        conversation_history: list = None
    ) -> dict:
        """Handle user interaction based on selected category"""
        
        # Select appropriate prompt based on category
        prompt_map = {
            "brochure": BROCHURE_ASSISTANT_PROMPT,
            "booking": BOOKING_ASSISTANT_PROMPT,
            "availability": AVAILABILITY_ASSISTANT_PROMPT,
            "question": FAQ_ASSISTANT_PROMPT,
            "other": FAQ_ASSISTANT_PROMPT
        }
        
        system_prompt = prompt_map.get(category, FAQ_ASSISTANT_PROMPT)
        
        # Format prompt with lead data
        formatted_prompt = system_prompt.format(
            name=lead_data.get("name", "User"),
            email=lead_data.get("email", ""),
            phone=lead_data.get("phone", ""),
            property_context="[Property database will be integrated in next step]",
            knowledge_context="[RAG system will be integrated in next step]"
        )
        
        # Build conversation context
        full_prompt = f"""{formatted_prompt}

        User's message: {user_message}

        Your response:"""
        
        # Generate AI response
        try:
            response = await gemini_service.generate_response(
                prompt=full_prompt,
                conversation_history=conversation_history or []
            )
            
            return {
                "message": response,
                "type": "assistant_response",
                "category": category
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "message": "I apologize, but I'm having trouble processing your request. Our agent will contact you shortly.",
                "type": "error",
                "category": category
            }
            
        def get_handoff_message(self, lead_data: dict) -> dict:
            """Return handoff/closing message"""
            return {
                "message": HANDOFF_MESSAGE.format(name=lead_data.get("name", "there")),
                "type": "handoff",
                "show_restart": True
            }
            
# Singleton instance
conversation_service_v2 = ConversationServiceV2()
    