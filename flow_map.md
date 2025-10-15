# BROCHURE FLOW

1. **BROCHURE\_START (after lead capture if not done before)**
    * > message="✅ Perfect! Your property brochure is on its way to your email.
    Let's find properties that match your needs! 🏡"

---

2. **BROCHURE\_PREFERENCES (only if preferences not collected before)**
    * message =  
    > "Please share your preferences:"
    * UI - [Form: **Budget** dropdown, **Location** chips, **Property type** buttons]

---

3. **BROCHURE\_PREFERENCES\_COLLECTED (only if BROCHURE\_PREFERENCES is responded with)**
    * message = 
    > "Great! Based on your preferences, we'll send you tailored recommendations"

---

5. **BROCHURE\_COMPLETE**
    * message = 
    > “Would you like to schedule a quick call with us?"
    * UI - [Options: **Book a Call** | **Maybe later** ]
    note: Maybe later option leads to assisstant reponse - "Is there anything else I can help you with?" and then show the main menu UI.

---

# CALL SCHEDULE FLOW

1. **BOOKING\_START (after lead capture if not done before)**
    * message=
    > ✅ Let's schedule your call with our property expert!  
    > Would you like to use the same contact number you provided earlier?
    * UI - [options - **Yes 👍** | **Use a different number ☎️**]

---

2. **BOOKING\_PREFERENCE (only if preferences not collected before)** 
    * message =  
    > "Please share your preferences:"
    * UI - [Form: **Budget** dropdown, **Location** chips, **Property type** buttons]

---

3. **BOOKING\_PREFERENCES\_COLLECTED (only if preBOOKING\_PREFERENCE is responded with)**
    * message = 
    > "Great! I’ve noted your preferences so our expert can be ready with suitable options. ✅"

---

4. **BOOKING\_CALL\_TIME\_PREFERENCE**
    * message =
    > "Which time would you prefer for the call?"
    * [UI: ☀️ Morning (9 AM – 12 PM)] [🌤️ Afternoon (12 PM – 4 PM)] [🌇 Evening (4 PM – 8 PM) buttons]

---

5. **BOOKING\_CONFIRMATION**
    * message = 
    > ✅ All set! Your appointment has been scheduled.  
    > Our property expert will call you at [phone] during the [selected time period].

---

6. **BOOKING\_COMPLETE**
    * message = 
    > "Is there anything else I can help you with?"
    * UI - [Options: **Ask a question** | **Back to Menu**]

---


# EXPLORE PROPERTIES FLOW

1. **EXPLORE_START**
    * > message="🏡 Let's find your ideal property!  
    Please choose the type of property you're interested in:"
    * [UI: Buttons - **Apartments**, **Villas**, **Residential Plots**, **Commercial Spaces**]

---

2. **EXPLORE_PROPERTY_TYPE_SELECTED (if property_count > 6)**
    * > message="Here are some available properties in **[selected_property_type]**."
    * [UI: Property Cards Carousel – show up to 6 cards with image, title, location, price, and buttons (**Get Brochure**, **Price Quote**)]
    * [UI: Buttons – **Show More Properties**, **Back to Menu**]

---

3. **EXPLORE_SHOW_MORE (if property count > 6 or if Show More Properties button is clicked)**
    * > message="To help narrow it down, please share your preferences (optional):"
    * [UI: Form – **Budget Range** dropdown/slider, **Preferred Location(s)** chips, **Bedrooms** dropdown, **Possession** (Ready/Upcoming), **Builder Preference** optional]
    * [UI: Submit Button – **Show Matching Properties**]

---

4. **EXPLORE_FILTERED_RESULTS**
    * > message="Here are the properties matching your preferences:"
    * [UI: Filtered Property Cards Carousel – show up to 6 at a time with left/right scroll]
    * [UI: Buttons – **Get Brochure**, **Price Quote**, **Show More Properties**, **Back to Menu**]

---

5. **EXPLORE_PROPERTY_ACTION (triggered by Get Brochure / Price Quote button if lead form not already filled)**
    * > message="Please provide your details so our team can share more info about this property."
    * [UI: Lead Form – **Name**, **Email**, **Mobile Number**]
    * After submission:
        * > message="✅ Got it! Our team will reach out soon with the details of your selected property."

---

6. **EXPLORE_PROPERTY_ACTION (triggered by Get Brochure / Price Quote button if lead form already filled)**
    * > message="✅ Our team will reach out soon with the details of your selected property."

---

6. **EXPLORE_AI_HANDOFF (optional – after browsing)**
    * > message="💬 Would you like to ask our AI Assistant any specific questions about these properties?"
    * [UI: Buttons – **Ask with AI**, **Back to Menu**]

---

# ASK A QUESTION FLOW

1. **ASK_START**
    * > message="💬 Sure! You can ask me anything about our properties, locations, prices, or availability.  
    I’ll do my best to help you out!"
    * [UI: Input field – “Type your question…”]
    * [UI: Suggested Questions (chips) –  
      “What are the ongoing projects near OMR?”,  
      “What’s the price of your 3BHK apartments?”,  
      “Do you have plots available in ECR?”,  
      “What’s the possession date for XYZ project?”]

---

2. **ASK_QUERY_RECEIVED**
    * > message="🔍 Let me check that for you..."
    * [AI: Query sent to RAG system (connected to brochure + project database)]
    * [UI: Typing animation while AI fetches the answer]

---

3. **ASK_RESPONSE**
    * > message="[AI-generated answer based on the user's question]"
    * [UI (could be potentially decided by the AI): Buttons – **Get Brochure**, **Book a Call**, **Explore Properties**]

---

4. **ASK_FOLLOWUP (if no user actions for 10 seconds)**
    * > message="Would you like me to help you further with this property?"
    * [UI: Buttons – **Get Brochure for this Project**, **Schedule a Call**, **Back to Menu**]

---






