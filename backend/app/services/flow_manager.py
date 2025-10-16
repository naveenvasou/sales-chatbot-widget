from typing import Dict, Any, Optional
from app.services.state_machine import state_machine, FlowState
from app.prompts.system_prompts import CATEGORIES

class FlowManager:
    """Manages conversation flow and state transitions"""
    
    def __init__(self):
        self.state_machine = state_machine
    
    def start_category_flow(self, category: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start flow for selected category"""
        
        category_to_state = {
            "brochure": FlowState.BROCHURE_SEND,
            "booking": FlowState.BOOKING_START,
            "explore": FlowState.EXPLORE_START,
            "question": FlowState.ASK_START
        }

        start_state = category_to_state.get(category, FlowState.ASK_START)
        
        context = {
            "name": lead_data.get("name", "there"),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", "")
        }
        
        # Get start state response
        start_response = self.state_machine.get_state_response(start_state, context)
        
        # IMPORTANT: If start state has no UI but next state does, fetch next state
        #if not start_response.ui_component and start_response.next_state:
        #    next_response = self.state_machine.get_state_response(start_response.next_state, context)
            
            # Combine messages
        #    combined_message = f"{start_response.message}\n\n{next_response.message}"
            
        #    return {
        #        "message": combined_message,
        #        "current_state": start_response.next_state.value,  # Use next state
        #        "next_state": next_response.next_state.value if next_response.next_state else None,
        #        "ui_component": self._serialize_ui_component(next_response.ui_component),
        #        "show_menu_button": next_response.show_menu_button,
        #        "requires_llm": next_response.requires_llm
        #    }
    
        # Otherwise return start state as-is
        return {
            "message": start_response.message,
            "current_state": start_state.value,
            "next_state": start_response.next_state.value if start_response.next_state else None,
            "ui_component": self._serialize_ui_component(start_response.ui_component),
            "show_menu_button": start_response.show_menu_button,
            "requires_llm": start_response.requires_llm
        }
    
    def handle_user_input(
        self,
        current_state: str,
        user_input: Any,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle user input in current state and transition to next"""
        
        try:
            state_enum = FlowState(current_state)
        except ValueError:
            state_enum = FlowState.GREETING
        
        # Special handling for EXPLORE_START (property type selection)
        if state_enum == FlowState.EXPLORE_START:
            property_type = user_input
            property_type_labels = {
                "apartment": "Apartments",
                "villa": "Villas",
                "plot": "Residential Plots",
                "commercial": "Commercial Spaces"
            }
            
            return {
                "message": f"Here are some available {property_type_labels.get(property_type, 'Properties')} in Chennai:",
                "current_state": FlowState.EXPLORE_PROPERTY_TYPE.value,
                "next_state": FlowState.EXPLORE_SHOW_MORE.value,
                "ui_component": {
                    "type": "property_cards",
                    "data": {
                        "property_type": property_type,
                        "limit": 6
                    }
                },
                "show_menu_button": True,
                "requires_llm": False
            }
        
        # Get next state
        next_state = self.state_machine.get_next_state(state_enum, user_input)
        
        if next_state=="handoff":
            if user_input["value"]=="explore_properties":
                next_state=FlowState.EXPLORE_START
            if user_input["value"]=="back_to_menu":
                categories = [
                        {
                            "id": key,
                            "label": value["label"],
                            "emoji": value["emoji"]
                        }
                        for key, value in CATEGORIES.items()
                    ]
                
                return {
                    "message": "",
                    "type": "greeting",
                    "show_categories": True,
                    "current_state":"greeting",
                    "next_state":"category_selection",
                    "ui_component":{
                        "type": "category_buttons",
                        "data": {
                            "categories":categories
                        }
                    },
                    "show_menu_button": False
                }
        
        # Prepare context with user input
        full_context = context or {}
        full_context.update(self._process_user_input(state_enum, user_input))
        
        # Get response for next state
        response = self.state_machine.get_state_response(next_state, full_context)
        
        return {
            "message": response.message,
            "current_state": next_state.value,
            "next_state": response.next_state.value if response.next_state else None,
            "ui_component": self._serialize_ui_component(response.ui_component),
            "show_menu_button": response.show_menu_button,
            "requires_llm": response.requires_llm,
            "user_data": full_context
        }
    
    def _process_user_input(self, state: FlowState, user_input: Any) -> Dict[str, Any]:
        """Process and structure user input based on state"""
        
        processed = {}
        
        if isinstance(user_input, dict):
            processed.update(user_input)
        elif isinstance(user_input, str):
            processed["user_response"] = user_input
            
            # Handle property type selection in Explore flow
            if state == FlowState.EXPLORE_START:
                processed["property_type"] = user_input
                processed["property_type_label"] = {
                    "apartment": "Apartments",
                    "villa": "Villas", 
                    "plot": "Residential Plots",
                    "commercial": "Commercial Spaces"
                }.get(user_input, "Properties")
        
        return processed
    
    def _serialize_ui_component(self, component) -> Optional[Dict[str, Any]]:
        """Serialize UI component to dict"""
        if not component:
            return None
        
        return {
            "type": component.type,
            "data": component.data
        }
    
    def go_to_main_menu(self) -> Dict[str, Any]:
        """Return to main menu (category selection)"""
        from app.services.conversation_service_v2 import conversation_service_v2
        
        greeting = conversation_service_v2.get_greeting()
        
        return {
            "message": "What else can I help you with? 🏠",
            "current_state": FlowState.CATEGORY_SELECTION.value,
            "next_state": None,
            "ui_component": {
                "type": "category_buttons",
                "data": {
                    "categories": greeting["categories"]
                }
            },
            "show_menu_button": False,
            "requires_llm": False
        }


# Singleton instance
flow_manager = FlowManager()