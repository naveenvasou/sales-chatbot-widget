from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class FlowState(str, Enum):
    """All possible states in the chatbot flow"""
    # Common states
    GREETING = "greeting"
    CATEGORY_SELECTION = "category_selection"
    LEAD_CAPTURE = "lead_capture"
    
    # Brochure flow
    BROCHURE_START = "brochure_start"
    BROCHURE_PREFERENCES = "brochure_preferences"
    BROCHURE_PREFERENCES_COLLECTED = "brochure_preferences_collected"
    BROCHURE_CONFIRMATION = "brochure_confirmation"
    BROCHURE_COMPLETE = "brochure_complete"
    
    # Booking flow
    BOOKING_START = "booking_start"
    BOOKING_PROPERTY_INTEREST = "booking_property_interest"
    BOOKING_DATE_PREFERENCE = "booking_date_preference"
    BOOKING_TIME_PREFERENCE = "booking_time_preference"
    BOOKING_SPECIAL_REQUESTS = "booking_special_requests"
    BOOKING_CONFIRMATION = "booking_confirmation"
    BOOKING_COMPLETE = "booking_complete"
    
    # Availability flow
    AVAILABILITY_START = "availability_start"
    AVAILABILITY_LOCATION = "availability_location"
    AVAILABILITY_BUDGET = "availability_budget"
    AVAILABILITY_PROPERTY_TYPE = "availability_property_type"
    AVAILABILITY_TIMELINE = "availability_timeline"
    AVAILABILITY_SEARCH = "availability_search"
    AVAILABILITY_RESULTS = "availability_results"
    AVAILABILITY_COMPLETE = "availability_complete"
    
    # FAQ flow
    FAQ_START = "faq_start"
    FAQ_CATEGORY_SELECT = "faq_category_select"
    FAQ_HANDLE = "faq_handle"
    FAQ_FOLLOWUP = "faq_followup"
    FAQ_COMPLETE = "faq_complete"
    
    # Other queries flow
    OTHER_START = "other_start"
    OTHER_INPUT = "other_input"
    OTHER_HANDLED = "other_handled"
    OTHER_COMPLETE = "other_complete"
    
    # Terminal states
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
        self.state_config = self._build_state_config()
    
    def _build_state_config(self) -> Dict[FlowState, StateResponse]:
        """Build configuration for all states"""
        return {
            # ====== BROCHURE FLOW ======
            FlowState.BROCHURE_START: StateResponse(
                message="✅ Perfect! Your property brochure is on its way to your email.\n\nLet's find properties that match your needs! 🏡",
                ui_component=None,
                next_state=FlowState.BROCHURE_PREFERENCES,
                show_menu_button=True
            ),
            
            FlowState.BROCHURE_PREFERENCES: StateResponse(
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
                                    {"value": "200_plus", "label": "₹2 Crore+"},
                                    {"value": "flexible", "label": "Flexible"}
                                ],
                                "required": True
                            },
                            {
                                "name": "location",
                                "label": "📍 Preferred Location",
                                "type": "multiselect_chips",
                                "options": ["Mumbai", "Chennai", "Bangalore", "Pune", "Hyderabad", "Delhi NCR"],
                                "required": True
                            },
                            {
                                "name": "property_type",
                                "label": "🏠 Property Type",
                                "type": "buttons",
                                "options": [
                                    {"value": "apartment", "label": "🏢 Apartment"},
                                    {"value": "villa", "label": "🏡 Villa"},
                                    {"value": "plot", "label": "📐 Plot"},
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
                message="Excellent! Based on your preferences:\n\n{preferences_summary}\n\nYou'll receive:\n✅ General property brochure\n✅ Personalized recommendations matching your criteria\n\nBoth will be sent to your email within the next few minutes!",
                ui_component=None,
                next_state=FlowState.BROCHURE_CONFIRMATION,
                show_menu_button=True
            ),
            
            FlowState.BROCHURE_CONFIRMATION: StateResponse(
                message="Is there anything specific you'd like to know about our properties?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "amenities", "label": "🏊 Amenities"},
                            {"value": "payment", "label": "💳 Payment Plans"},
                            {"value": "possession", "label": "🔑 Possession Timeline"},
                            {"value": "nothing", "label": "Nothing, I'm good!"}
                        ]
                    }
                ),
                next_state=FlowState.BROCHURE_COMPLETE,
                show_menu_button=True
            ),
            
            FlowState.BROCHURE_COMPLETE: StateResponse(
                message="Perfect! Our team will reach out to you soon with detailed information.\n\nThank you for your interest! 🙏",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "menu", "label": "🏠 Back to Main Menu"},
                            {"value": "end", "label": "👋 End Chat"}
                        ]
                    }
                ),
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            
            # ====== BOOKING FLOW ======
            FlowState.BOOKING_START: StateResponse(
                message="✅ Great! Let's schedule your site visit! 📅\n\nAre you interested in visiting a specific property?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "specific", "label": "Yes, specific property"},
                            {"value": "any", "label": "Show me options"},
                            {"value": "not_sure", "label": "Not sure yet"}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_PROPERTY_INTEREST,
                show_menu_button=True
            ),
            
            FlowState.BOOKING_PROPERTY_INTEREST: StateResponse(
                message="When would you prefer to visit?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "this_week", "label": "📅 This Week"},
                            {"value": "next_week", "label": "📅 Next Week"},
                            {"value": "flexible", "label": "🤷 Flexible"}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_DATE_PREFERENCE,
                show_menu_button=True
            ),
            
            FlowState.BOOKING_DATE_PREFERENCE: StateResponse(
                message="What time works best for you?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "morning", "label": "🌅 Morning (9 AM - 12 PM)"},
                            {"value": "afternoon", "label": "☀️ Afternoon (12 PM - 4 PM)"},
                            {"value": "evening", "label": "🌆 Evening (4 PM - 7 PM)"}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_TIME_PREFERENCE,
                show_menu_button=True
            ),
            
            FlowState.BOOKING_TIME_PREFERENCE: StateResponse(
                message="Any special requests or requirements for the visit? (Optional)",
                ui_component=UIComponent(
                    type="text_input",
                    data={
                        "placeholder": "E.g., Need wheelchair access, want to see specific floor plans...",
                        "optional": True,
                        "skip_label": "No special requests"
                    }
                ),
                next_state=FlowState.BOOKING_SPECIAL_REQUESTS,
                show_menu_button=True
            ),
            
            FlowState.BOOKING_SPECIAL_REQUESTS: StateResponse(
                message="✅ Perfect! Your site visit has been scheduled!\n\n📋 Summary:\n{booking_summary}\n\nOur agent will call you at {phone} to confirm the exact date and time.\n\nLooking forward to showing you our properties! 🏡",
                ui_component=None,
                next_state=FlowState.BOOKING_CONFIRMATION,
                show_menu_button=True
            ),
            
            FlowState.BOOKING_CONFIRMATION: StateResponse(
                message="Would you like to do anything else?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "brochure", "label": "📋 Get Brochure"},
                            {"value": "menu", "label": "🏠 Main Menu"},
                            {"value": "end", "label": "👋 End Chat"}
                        ]
                    }
                ),
                next_state=FlowState.BOOKING_COMPLETE,
                show_menu_button=False
            ),
            
            FlowState.BOOKING_COMPLETE: StateResponse(
                message="Thank you! We'll be in touch soon! 🙏",
                ui_component=None,
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            
            # ====== AVAILABILITY FLOW ======
            FlowState.AVAILABILITY_START: StateResponse(
                message="Let's find the perfect property for you! 🔍\n\nWhere are you looking to buy?",
                ui_component=UIComponent(
                    type="multiselect_chips",
                    data={
                        "label": "📍 Select Location(s)",
                        "options": ["Mumbai", "Chennai", "Bangalore", "Pune", "Hyderabad", "Delhi NCR", "Other"],
                        "allow_multiple": True
                    }
                ),
                next_state=FlowState.AVAILABILITY_LOCATION,
                show_menu_button=True
            ),
            
            FlowState.AVAILABILITY_LOCATION: StateResponse(
                message="What's your budget range?",
                ui_component=UIComponent(
                    type="dropdown",
                    data={
                        "label": "💰 Budget Range",
                        "options": [
                            {"value": "under_50", "label": "Under ₹50 Lakhs"},
                            {"value": "50_100", "label": "₹50L - ₹1 Crore"},
                            {"value": "100_200", "label": "₹1 Cr - ₹2 Crore"},
                            {"value": "200_plus", "label": "₹2 Crore+"}
                        ]
                    }
                ),
                next_state=FlowState.AVAILABILITY_BUDGET,
                show_menu_button=True
            ),
            
            FlowState.AVAILABILITY_BUDGET: StateResponse(
                message="What type of property are you interested in?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "apartment", "label": "🏢 Apartment"},
                            {"value": "villa", "label": "🏡 Villa"},
                            {"value": "plot", "label": "📐 Plot"},
                            {"value": "commercial", "label": "🏪 Commercial"}
                        ]
                    }
                ),
                next_state=FlowState.AVAILABILITY_PROPERTY_TYPE,
                show_menu_button=True
            ),
            
            FlowState.AVAILABILITY_PROPERTY_TYPE: StateResponse(
                message="When are you planning to make a decision?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "urgent", "label": "🔥 Urgent (This month)"},
                            {"value": "soon", "label": "📅 Soon (1-3 months)"},
                            {"value": "later", "label": "⏰ Later (3-6 months)"},
                            {"value": "exploring", "label": "🔍 Just exploring"}
                        ]
                    }
                ),
                next_state=FlowState.AVAILABILITY_TIMELINE,
                show_menu_button=True
            ),
            
            FlowState.AVAILABILITY_TIMELINE: StateResponse(
                message="🔍 Searching for properties matching your criteria...\n\n{search_summary}",
                ui_component=None,
                next_state=FlowState.AVAILABILITY_SEARCH,
                show_menu_button=True,
                requires_llm=False  # Can use RAG here if we have property DB
            ),
            
            FlowState.AVAILABILITY_SEARCH: StateResponse(
                message="Based on your requirements, we have several options available!\n\nOur agent will send detailed property listings with:\n✅ Photos & floor plans\n✅ Pricing & payment options\n✅ Availability status\n\nto your email: {email}",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "callback", "label": "📞 Request Callback"},
                            {"value": "visit", "label": "📅 Schedule Visit"},
                            {"value": "menu", "label": "🏠 Main Menu"}
                        ]
                    }
                ),
                next_state=FlowState.AVAILABILITY_RESULTS,
                show_menu_button=False
            ),
            
            FlowState.AVAILABILITY_RESULTS: StateResponse(
                message="Perfect! We'll be in touch with detailed information soon! 🙏",
                ui_component=None,
                next_state=FlowState.AVAILABILITY_COMPLETE,
                show_menu_button=False
            ),
            
            FlowState.AVAILABILITY_COMPLETE: StateResponse(
                message="Thank you for your interest!",
                ui_component=None,
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            
            # ====== FAQ FLOW ======
            FlowState.FAQ_START: StateResponse(
                message="I'm here to answer your questions! 💬\n\nWhat would you like to know about?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "loan", "label": "💰 Loans & Finance"},
                            {"value": "amenities", "label": "🏊 Amenities"},
                            {"value": "documentation", "label": "📄 Documentation"},
                            {"value": "possession", "label": "🔑 Possession Timeline"},
                            {"value": "custom", "label": "❓ Other Question"}
                        ]
                    }
                ),
                next_state=FlowState.FAQ_CATEGORY_SELECT,
                show_menu_button=True
            ),
            
            FlowState.FAQ_CATEGORY_SELECT: StateResponse(
                message="",  # Will be filled by FAQ handler
                ui_component=None,
                next_state=FlowState.FAQ_HANDLE,
                show_menu_button=True,
                requires_llm=True  # LLM + RAG used here
            ),
            
            FlowState.FAQ_HANDLE: StateResponse(
                message="Is there anything else I can help you with?",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "another", "label": "❓ Ask Another Question"},
                            {"value": "agent", "label": "💬 Talk to Agent"},
                            {"value": "menu", "label": "🏠 Main Menu"}
                        ]
                    }
                ),
                next_state=FlowState.FAQ_FOLLOWUP,
                show_menu_button=False
            ),
            
            FlowState.FAQ_FOLLOWUP: StateResponse(
                message="Thank you! Our team is here to help! 🙏",
                ui_component=None,
                next_state=FlowState.FAQ_COMPLETE,
                show_menu_button=False
            ),
            
            FlowState.FAQ_COMPLETE: StateResponse(
                message="",
                ui_component=None,
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            
            # ====== OTHER QUERIES ======
            FlowState.OTHER_START: StateResponse(
                message="Please tell me what you're looking for, and I'll do my best to help! 💬",
                ui_component=UIComponent(
                    type="text_input",
                    data={
                        "placeholder": "Type your question or query..."
                    }
                ),
                next_state=FlowState.OTHER_INPUT,
                show_menu_button=True
            ),
            
            FlowState.OTHER_INPUT: StateResponse(
                message="Thank you for your query. Our agent will contact you shortly to assist with: \"{query}\"",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "menu", "label": "🏠 Main Menu"},
                            {"value": "end", "label": "👋 End Chat"}
                        ]
                    }
                ),
                next_state=FlowState.OTHER_HANDLED,
                show_menu_button=False
            ),
            
            FlowState.OTHER_HANDLED: StateResponse(
                message="We'll be in touch soon! 🙏",
                ui_component=None,
                next_state=FlowState.OTHER_COMPLETE,
                show_menu_button=False
            ),
            
            FlowState.OTHER_COMPLETE: StateResponse(
                message="",
                ui_component=None,
                next_state=FlowState.HANDOFF,
                show_menu_button=False
            ),
            
            # ====== TERMINAL STATES ======
            FlowState.HANDOFF: StateResponse(
                message="Thank you for chatting with us! Our team will be in touch soon. Have a great day! 🙏✨",
                ui_component=UIComponent(
                    type="buttons",
                    data={
                        "options": [
                            {"value": "restart", "label": "🔄 Start Over"},
                            {"value": "end", "label": "👋 Close Chat"}
                        ]
                    }
                ),
                next_state=FlowState.ENDED,
                show_menu_button=False
            ),
        }
    
    def get_state_response(
        self,
        state: FlowState,
        context: Dict[str, Any] = None
    ) -> StateResponse:
        """Get response for a given state with context"""
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