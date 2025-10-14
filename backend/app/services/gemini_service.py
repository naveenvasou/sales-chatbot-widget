import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.gemini_model)
        
    async def generate_response(self, prompt: str, conversation_history: list = None) -> str:
        """
        Generate a response using Gemini
        
        Args:
            prompt: User's message
            conversation_history: List of previous messages (optional)
        
        Returns:
            AI generated response
        """
        try:
            # Start a chat session
            chat = self.model.start_chat(history=conversation_history or [])
            
            # Generate response
            response = chat.send_message(prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble connecting right now. Please try again in a moment."
    
    async def test_connection(self) -> dict:
        """Test if Gemini API is working"""
        try:
            response = await self.generate_response("Say 'Connection successful!' if you can read this.")
            return {
                "status": "success",
                "message": "Gemini API connected successfully",
                "test_response": response
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Gemini: {str(e)}"
            }

# Create a singleton instance
gemini_service = GeminiService()