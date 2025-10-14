from app.services.gemini_service import gemini_service

import json
import re


class ConversationService:
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: list,
        lead_data: dict = None
    ) -> dict:
        """
        Generate AI response with context awareness
        
        Returns:
            {
                "response": str,
                "stage": str,
                "extracted_data": dict
            }
        """
        
        # Determine conversation stage
        stage = await self._detect_conversation_stage(conversation_history)
        
        # Extract any new lead information from user message
        extracted_data = await self._extract_lead_data(conversation_history + [
            {"role": "user", "parts": [user_message]}
        ])
        
        # Build context-aware prompt
        full_prompt = self._build_conversation_prompt(
            user_message=user_message,
            conversation_history=conversation_history,
            stage=stage,
            lead_data={**(lead_data or {}), **extracted_data}
        )
        
        # Generate response
        response = await gemini_service.generate_response(
            prompt=full_prompt,
            conversation_history=conversation_history
        )
        
        return {
            "response": response,
            "stage": stage,
            "extracted_data": extracted_data
        }
    
    def _build_conversation_prompt(
        self,
        user_message: str,
        conversation_history: list,
        stage: str,
        lead_data: dict
    ) -> str:
        """Build a context-aware prompt for the AI"""
        
        # Get contextual guidance based on stage
        stage_guidance = get_contextual_prompt(stage, lead_data)
        
        prompt = f"""{REAL_ESTATE_SYSTEM_PROMPT}

        ---
        CURRENT CONVERSATION STAGE: {stage}

        STAGE GUIDANCE:
        {stage_guidance}

        ---
        LEAD INFORMATION COLLECTED SO FAR:
        {json.dumps(lead_data, indent=2)}

        ---
        USER'S LATEST MESSAGE:
        {user_message}

        ---
        Generate your response as Maya. Remember to:
        1. Stay in character
        2. Follow the stage guidance
        3. Ask only ONE question if needed
        4. Be natural and conversational
        5. Acknowledge information they've already shared

        Your response:"""
        
        return prompt
    
    async def _detect_conversation_stage(self, conversation_history: list) -> str:
        """Detect what stage the conversation is at"""
        
        if not conversation_history or len(conversation_history) < 2:
            return "GREETING"
        
        # Format conversation for analysis
        conversation_text = self._format_conversation_history(conversation_history)
        
        prompt = CONVERSATION_STAGE_PROMPT.format(
            conversation_history=conversation_text
        )
        
        try:
            stage = await gemini_service.generate_response(prompt)
            stage = stage.strip().upper()
            
            # Validate stage
            valid_stages = ["GREETING", "PURPOSE_DISCOVERY", "QUALIFICATION", 
                          "VALUE_OFFER", "CONTACT_CAPTURE", "CLOSING"]
            
            if stage in valid_stages:
                return stage
            else:
                return "QUALIFICATION"  # Default fallback
                
        except Exception as e:
            print(f"Error detecting stage: {e}")
            return "QUALIFICATION"
    
    async def _extract_lead_data(self, conversation_history: list) -> dict:
        """Extract lead information from conversation"""
        
        conversation_text = self._format_conversation_history(conversation_history)
        
        prompt = LEAD_EXTRACTION_PROMPT.format(
            conversation_history=conversation_text
        )
        
        try:
            response = await gemini_service.generate_response(prompt)
            
            # Clean the response - remove markdown code blocks if present
            cleaned_response = response.strip()
            
            # Remove markdown code blocks
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0]
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0]
            
            # Extract JSON from response
            cleaned_response = cleaned_response.strip()
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                lead_data = json.loads(json_str)
                
                # Clean up null values and empty strings
                return {k: v for k, v in lead_data.items() if v is not None and v != ""}
            
            return {}
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {je}")
            print(f"Response was: {response}")
            return {}
        except Exception as e:
            print(f"Error extracting lead data: {e}")
            print(f"Response was: {response if 'response' in locals() else 'No response'}")
            return {}
    
    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history for prompts"""
        formatted = []
        for msg in history[-10:]:  # Last 10 messages for context
            role = "User" if msg["role"] == "user" else "Maya"
            content = msg["parts"][0] if isinstance(msg["parts"], list) else msg["parts"]
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)


# Singleton instance
conversation_service = ConversationService()