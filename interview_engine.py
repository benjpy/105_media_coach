class InterviewSession:
    def __init__(self):
        self.transcript = [] # List of {'question': str, 'answer': str}
        self.current_question = None
        self.journalist_image = None
        self.logo_image = None
        self.startup_description = ""
        self.persona = ""
        self.difficulty = ""
        self.news_context = ""
        self.is_active = False
        self.evaluation = None

    def start_session(self, startup_description, persona, difficulty, news_context, journalist_img, logo_img):
        self.startup_description = startup_description
        self.persona = persona
        self.difficulty = difficulty
        self.news_context = news_context
        self.journalist_image = journalist_img
        self.logo_image = logo_img
        self.transcript = []
        self.is_active = True
        self.evaluation = None

    def add_turn(self, question, answer):
        self.transcript.append({'question': question, 'answer': answer})

    def set_current_question(self, question):
        self.current_question = question

    def end_session(self):
        self.is_active = False
