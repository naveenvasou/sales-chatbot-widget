from app.services.gemini_service import gemini_service
from app.services.property_service import property_service
import json

class AIService:
    
    async def answer_question(self, question: str, conversation_history: list = None) -> str:
        """Answer user question using property context + LLM"""
        
        # Get property context (simple keyword matching for now)
        property_context = self._get_relevant_properties(question)
        
        # Build prompt with context
        prompt = f"""You are Maya, a helpful real estate assistant for DreamHome Realty in Chennai.

USER QUESTION: {question}

AVAILABLE PROPERTIES CONTEXT:
{property_context}

Instructions:
- Answer the user's question using ONLY the property information provided above
- Be conversational and helpful
- If you don't have the information, say "I don't have that specific information, but our agent can help you with that."
- Keep response to 2-3 sentences
- If relevant, mention specific properties by name

Your response:"""
        
        response = await gemini_service.generate_response(
            prompt=prompt,
            conversation_history=conversation_history or []
        )
        
        return response
    
    def _get_relevant_properties(self, question: str) -> str:
        """Get relevant properties based on question keywords"""
        question_lower = question.lower()
        
        # Simple keyword matching
        all_properties = property_service.properties
        relevant = []
        
        # Filter by keywords
        if "omr" in question_lower:
            relevant = [p for p in all_properties if "OMR" in p.get("location", "")]
        elif "ecr" in question_lower:
            relevant = [p for p in all_properties if "ECR" in p.get("location", "")]
        elif "villa" in question_lower:
            relevant = [p for p in all_properties if p.get("type") == "villa"]
        elif "apartment" in question_lower:
            relevant = [p for p in all_properties if p.get("type") == "apartment"]
        else:
            relevant = all_properties[:5]  # Show first 5 by default
        
        # Format properties for context
        if not relevant:
            return "No specific properties match this query."
        
        context = []
        for p in relevant[:3]:  # Limit to 3 for token efficiency
            context.append(f"""
Property: {p.get('name')}
Type: {p.get('type')}
Location: {p.get('location')}
Price: ₹{p.get('price')}
Bedrooms: {p.get('bedrooms', 'N/A')}
Description: {p.get('description', 'N/A')}
""")
        
        return "\n".join(context)

# Singleton
ai_service = AIService()