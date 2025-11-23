import os
import datetime
import google.generativeai as genai
import json
import streamlit as st

# Local version
def configure_genai():
    try:
        # Try to get key from Streamlit secrets
        api_key = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        # Fallback to environment variable
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in Streamlit secrets or environment variables.")

    genai.configure(api_key=api_key)


def generate_outlet_name(persona, startup_description):
    """Generates a fictional news outlet name."""
    configure_genai()
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Generate a creative, realistic name for a news outlet based on the following:
    Journalist Persona: {persona}
    Startup Topic: {startup_description}
    
    The name should sound professional and fit the persona (e.g., TechCrunch style for tech, Forbes style for business).
    Output ONLY the name.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

class JournalistAgent:
    def __init__(self, persona, difficulty, startup_description, news_context=None):
        self.persona = persona
        self.difficulty = difficulty
        self.startup_description = startup_description
        self.news_context = news_context
        configure_genai()
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_question(self, history):
        """
        Generates the next question based on the interview history.
        history: List of dicts {'question': str, 'answer': str}
        """
        
        # Log request
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("requests.txt", "a") as f:
            f.write(f"[{timestamp}] Persona: {self.persona}, History Length: {len(history)}\n")

        system_prompt = f"""
        You are a professional journalist conducting an interview with a startup founder.
        
        **Your Persona:** {self.persona}
        **Difficulty Level:** {self.difficulty} (Adjust your tone and skepticism accordingly)
        **Startup Description:** {self.startup_description}
        **News Context:** {self.news_context if self.news_context else "None"}
        
        **Instructions:**
        1. Ask ONE clear, relevant question.
        2. Do not repeat previous questions.
        3. If this is the first question, start with a standard opening relevant to the startup.
        4. If there is history, follow up on the previous answer or pivot to a new relevant topic.
        5. Keep the question realistic and challenging but fair (based on difficulty).
        6. Output ONLY the question text.
        """
        
        history_text = ""
        if history:
            history_text = "\n**Interview History:**\n"
            for i, turn in enumerate(history):
                history_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {turn['answer']}\n"
        
        full_prompt = system_prompt + history_text + "\n\n**Next Question:**"
        
        response = self.model.generate_content(full_prompt)
        return response.text.strip()

class EvaluatorAgent:
    def __init__(self):
        configure_genai()
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def evaluate_interview(self, transcript, startup_description):
        """
        Evaluates the full transcript.
        transcript: List of dicts {'question': str, 'answer': str}
        """
        
        transcript_text = ""
        for i, turn in enumerate(transcript):
            transcript_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {turn['answer']}\n"
            
        prompt = f"""
        You are an expert PR consultant and media coach. Evaluate the following interview transcript for a startup founder.
        
        **Startup Description:** {startup_description}
        
        **Transcript:**
        {transcript_text}
        
        **Task:**
        Analyze the founder's performance and provide a structured evaluation in JSON format with the following fields:
        
        1.  `strengths`: List of strings (what they did well).
        2.  `weaknesses`: List of strings (areas for improvement).
        3.  `score`: Integer 1-10 (overall performance).
        4.  `quotes`: List of strings (best/worst quotes from the founder).
        5.  `risky_statements`: List of strings (anything that could be taken out of context or damage reputation).
        6.  `rewrites`: List of objects {{'original': str, 'better': str}} (suggested improvements for specific answers).
        7.  `headline`: String (a likely headline a journalist would write based on this interview).
        8.  `training_plan`: List of strings (7-day plan to improve).
        
        **Output JSON ONLY.**
        """
        
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails, though response_mime_type should prevent this
            return {"error": "Failed to parse evaluation", "raw_text": response.text}
