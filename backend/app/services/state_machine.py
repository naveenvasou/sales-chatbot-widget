from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class FlowState(str, Enum):
    """All possible states"""
    # Common
    GREETING = "greeting"
    CATEGORY_SELECTION = "category_selection"
    LEAD_CAPTURE = "lead_capture"
    
    # Brochure flow
    BROCHURE_SEND = "brochure_send"
    BROCHURE_COMPLETE = "brochure_complete"
    
    # Call schedule flow
    BOOKING_START = "booking_start"
    BOOKING_TIME_SELECTION = "booking_time_selection"
    BOOKING_CONFIRMATION = "booking_confirmation"
 
    
    # Explore properties flow
    EXPLORE_START = "explore_start"
    EXPLORE_PROPERTY_TYPE = "explore_property_type"
    EXPLORE_SHOW_MORE = "explore_show_more"
    EXPLORE_FILTERED_RESULTS = "explore_filtered_results"
    EXPLORE_PROPERTY_ACTION = "explore_property_action"
    
    # Ask AI flow
    ASK_START = "ask_start"
    ASK_QUERY_RECEIVED = "ask_query_received"
    ASK_RESPONSE = "ask_response"
    ASK_FOLLOWUP = "ask_followup"
    
    # Terminal
    HANDOFF = "handoff"
    ENDED = "ended"


@dataclass
class UIComponent:
    """Defines a UI component to show in chat"""
    type: str  # "buttons", "form", "dropdown", "multiselect", "text_input", "date_picker"
    data: Dict[str, Any]
    
    
@dataclass
class StateResponse:
    """Response for a given state"""
    message: str
    ui_component: Optional[UIComponent] = None
    next_state: Optional[FlowState] = None
    show_menu_button: bool = True
    requires_llm: bool = False
    metadata: Dict[str, Any] = None


class StateMachine:
    """Manages chatbot state transitions and responses"""
    
    def __init__(self):
        self.lead_context = {"name":None, "email":None, "phone":None}
        self.state_config = self._build_state_config()
        
    
    def _build_state_config(self) -> Dict[FlowState, StateResponse]:
        """Build configuration for all states"""
        return {
            # ====== BROCHURE FLOW ======
            FlowState.BROCHURE_SEND: StateResponse(
                message="✅ Perfect! Our brochure is on its way to your email.",
                ui_component=None,
                next_state=FlowState.BROCHURE_COMPLETE,
                show_menu_button=True
            ),
            
            FlowState.BROCHURE_COMPLETE: StateResponse(
                message="Let's find properties that match your needs! 🏡",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "explore_properties ", "label": "Explore Properties"},
                            {"value": "back_to_menu", "label": "Back to Menu"}
                        ]
                    }
                ),
                next_state=FlowState.HANDOFF,
                show_menu_button=True
            ),
            
            """ FlowState.BROCHURE_PREFERENCES: StateResponse(
                message="Please share your preferences:",
                ui_component=UIComponent(
                    type="preference_form",
                    data={
                        "fields": [
                            {
                                "name": "budget",
                                "label": "💰 Budget Range",
                                "type": "dropdown",
                                "options": [
                                    {"value": "under_50", "label": "Under ₹50 Lakhs"},
                                    {"value": "50_100", "label": "₹50L - ₹1 Crore"},
                                    {"value": "100_200", "label": "₹1 Cr - ₹2 Crore"},
                                    {"value": "200_plus", "label": "₹2 Crore+"}
                                ],
                                "required": True
                            },
                            {
                                "name": "location",
                                "label": "📍 Preferred Location",
                                "type": "multiselect_chips",
                                "options": ["OMR", "ECR", "Velachery", "Anna Nagar", "T Nagar"],
                                "required": True
                            },
                            {
                                "name": "property_type",
                                "label": "🏠 Property Type",
                                "type": "buttons",
                                "options": [
                                    {"value": "apartment", "label": "🏢 Apartments"},
                                    {"value": "villa", "label": "🏡 Villas"},
                                    {"value": "plot", "label": "📐 Plots"},
                                    {"value": "commercial", "label": "🏪 Commercial"}
                                ],
                                "required": True
                            }
                        ],
                        "submit_label": "Find Properties"
                    }
                ),
                next_state=FlowState.BROCHURE_PREFERENCES_COLLECTED,
                show_menu_button=True
            ),
            
            FlowState.BROCHURE_PREFERENCES_COLLECTED: StateResponse(
                message="Great! Based on your preferences, we'll send you tailored recommendations.",
                ui_component=None,
                next_state=FlowState.BROCHURE_COMPLETE,
                show_menu_button=True
            ), """ : '',
            
            
            # ====== CALL SCHEDULE FLOW ======
            FlowState.BOOKING_START: StateResponse(
                message="Great! Let’s schedule a quick call with our property expert.",
                ui_component=UIComponent(
                    type="number_confirmation",
                    data={
                        "fields": [
                            {"name": "number_field", "label": str(self.lead_context["phone"]), "options": [{"value": "confirm", "label": "Continue"}]}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_TIME_SELECTION,
                show_menu_button=True
            ),
            FlowState.BOOKING_TIME_SELECTION: StateResponse(
                message="When works best for you?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "morning", "label": "🌞 Morning (9 AM – 12 PM)"},
                            {"value": "afternoon", "label": "☀️ Afternoon (12 PM – 4 PM)"},
                            {"value": "evening", "label": "🌇 Evening (4 PM – 8 PM)"}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_CONFIRMATION,
                show_menu_button=True
            ),
            FlowState.BOOKING_CONFIRMATION: StateResponse(
                message="✅ All set! Your appointment has been scheduled.\n\nOur property expert will call you during the {time_slot}.",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                            "options": [
                            {"value": "explore_properties", "label": "🏡 Explore Properties"},
                            {"value": "back_to_menu", "label": "🏠 Back to Menu"}
                            ]
                        }
                ),
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            # ====== EXPLORE PROPERTIES FLOW ======
            FlowState.EXPLORE_START: StateResponse(
                message="🏡 Let's find your ideal property!\n\nPlease choose the type of property you're interested in:",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "apartment", "label": "🏢 Apartments"},
                            {"value": "villa", "label": "🏡 Villas"},
                            {"value": "plot", "label": "📐 Residential Plots"},
                            {"value": "commercial", "label": "🏪 Commercial Spaces"}
                        ]
                    }
                ),
                next_state=FlowState.EXPLORE_PROPERTY_TYPE,
                show_menu_button=True
            ),
            FlowState.EXPLORE_PROPERTY_TYPE: StateResponse(
            message="Here are some available {property_type_label} in Chennai:",
            ui_component=UIComponent(
                type="property_cards",
                data={
                    "property_type": "{property_type}",
                    "limit": 6
                }
            ),
            next_state=FlowState.EXPLORE_SHOW_MORE,
            show_menu_button=True
            ),
            FlowState.EXPLORE_SHOW_MORE: StateResponse(
                message="Want to see more properties? Let me know your preferences to narrow it down:",
                ui_component=UIComponent(
                    type="preference_form",
                    data={
                        "fields": [
                            {
                                "name": "budget",
                                "label": "💰 Budget Range",
                                "type": "dropdown",
                                "options": [
                                    {"value": "under_50", "label": "Under ₹50 Lakhs"},
                                    {"value": "50_100", "label": "₹50L - ₹1 Crore"},
                                    {"value": "100_200", "label": "₹1 Cr - ₹2 Crore"},
                                    {"value": "200_plus", "label": "₹2 Crore+"}
                                ],
                                "required": False
                            },
                            {
                                "name": "location",
                                "label": "📍 Preferred Location",
                                "type": "multiselect_chips",
                                "options": ["OMR", "ECR", "Velachery", "Anna Nagar", "T Nagar"],
                                "required": False
                            }
                        ],
                        "submit_label": "Show Matching Properties"
                    }
                ),
                next_state=FlowState.EXPLORE_FILTERED_RESULTS,
                show_menu_button=True
            ),

            FlowState.EXPLORE_FILTERED_RESULTS: StateResponse(
                message="Here are the properties matching your preferences:",
                ui_component=UIComponent(
                    type="property_cards",
                    data={
                        "filtered": True,
                        "preferences": "{preferences}"
                    }
                ),
                next_state=FlowState.EXPLORE_PROPERTY_ACTION,
                show_menu_button=True
            ),

            FlowState.EXPLORE_PROPERTY_ACTION: StateResponse(
                message="✅ Got it! Our team will reach out soon with detailed information about this property.",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "another", "label": "🏡 See More Properties"},
                            {"value": "menu", "label": "🏠 Back to Menu"}
                        ]
                    }
                ),
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            # ====== ASK AI FLOW ======
            FlowState.ASK_START: StateResponse(
                message="💬 Sure! You can ask me anything about our properties, locations, prices, or availability.\n\nI'll do my best to help you out!\n\n💡 Try asking questions using the input field below:",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "omr_projects", "label": "Projects near OMR?"},
                            {"value": "3bhk_price", "label": "3BHK apartment prices?"},
                            {"value": "ecr_plots", "label": "Plots in ECR?"}
                        ]
                    }
                ),
                next_state=FlowState.ASK_QUERY_RECEIVED,
                show_menu_button=True,
                requires_llm=False
            ),

            FlowState.ASK_QUERY_RECEIVED: StateResponse(
                message="🔍 Let me check that for you...",
                ui_component=None,
                next_state=FlowState.ASK_RESPONSE,
                show_menu_button=True,
                requires_llm=True  # This will trigger RAG + LLM
            ),

            FlowState.ASK_RESPONSE: StateResponse(
                message="{ai_response}",  # Will be filled by LLM
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "brochure", "label": "📋 Get Brochure"},
                            {"value": "callback", "label": "📞 Schedule Call"},
                            {"value": "another_q", "label": "❓ Ask Another"}
                        ]
                    }
                ),
                next_state=FlowState.ASK_FOLLOWUP,
                show_menu_button=True,
                requires_llm=False
            ),

            FlowState.ASK_FOLLOWUP: StateResponse(
                message="Would you like me to help you further?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "menu", "label": "🏠 Main Menu"},
                            {"value": "end", "label": "👋 End Chat"}
                        ]
                    }
                ),
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
        }
    
    def get_state_response(
        self,
        state: FlowState,
        context: Dict[str, Any] = None
    ) -> StateResponse:
        """Get response for a given state with context"""
        self.lead_context = context
        self.state_config = self._build_state_config()
        response = self.state_config.get(state)
        
        if not response:
            raise ValueError(f"Unknown state: {state}")
        
        # Format message with context if provided
        if context and response.message:
            try:
                response.message = response.message.format(**context)
            except KeyError:
                pass  # Message doesn't need formatting
        
        return response
    
    def get_next_state(
        self,
        current_state: FlowState,
        user_action: str = None
    ) -> FlowState:
        """Determine next state based on current state and user action"""
        response = self.state_config.get(current_state)
        
        if response and response.next_state:
            return response.next_state
        
        return current_state


# Singleton instance
state_machine = StateMachine()