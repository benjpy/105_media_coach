import datetime
import os

class InterviewSession:
    def __init__(self):
        self.transcript = [] # List of {'question': str, 'answer': str}
        self.current_question = None
        self.journalist_name = ""
        self.outlet_name = ""
        self.startup_description = ""
        self.persona = ""
        self.difficulty = ""
        self.news_context = ""
        self.is_active = False
        self.evaluation = None

    def start_session(self, startup_description, persona, difficulty, news_context, journalist_name, outlet_name):
        self.startup_description = startup_description
        self.persona = persona
        self.difficulty = difficulty
        self.news_context = news_context
        self.journalist_name = journalist_name
        self.outlet_name = outlet_name
        self.transcript = []
        self.is_active = True
        self.evaluation = None

    def add_turn(self, question, answer):
        self.transcript.append({'question': question, 'answer': answer})

    def set_current_question(self, question):
        self.current_question = question

    def end_session(self):
        self.is_active = False

    def save_transcript(self):
        if not self.transcript:
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"startup_{timestamp}.txt"
        
        header = f"""Interviewer Type: {self.persona}
Difficulty Level: {self.difficulty}
News Context: {self.news_context}
Startup Description: {self.startup_description}
--------------------------------------------------
"""
        
        transcript_text = ""
        for i, turn in enumerate(self.transcript):
            transcript_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {turn['answer']}\n\n"
            
        with open(filename, "w") as f:
            f.write(header + transcript_text)
