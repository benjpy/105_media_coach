import streamlit as st
import os
from dotenv import load_dotenv
from image_gen import generate_assets
from stt import transcribe_audio
from agents import JournalistAgent, EvaluatorAgent, generate_outlet_name
from interview_engine import InterviewSession

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="PressCoach",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'session' not in st.session_state:
    st.session_state.session = InterviewSession()
if 'journalist_agent' not in st.session_state:
    st.session_state.journalist_agent = None

# Sidebar Inputs
with st.sidebar:
    st.title("🎙️ PressCoach")
    st.markdown("### Setup Interview")
    
    # Load startup description from file if available
    default_desc = ""
    if os.path.exists("startup.txt"):
        try:
            with open("startup.txt", "r") as f:
                default_desc = f.read().strip()
        except:
            pass

    startup_desc = st.text_area("Startup Description", value=default_desc, height=150, placeholder="e.g. We are building an AI that helps...")
    
    persona = st.selectbox(
        "Journalist Persona",
        ["TechCrunch (Skeptical, Technical)", "Forbes (Business-focused, Friendly)", "The Verge (Consumer-focused, Trendy)", "Investigative (Aggressive, Fact-checking)"]
    )
    
    difficulty = st.select_slider(
        "Difficulty",
        options=["Easy", "Medium", "Hard", "Nightmare"]
    )
    
    news_context = st.text_input("News Context (Optional)", placeholder="e.g. Recent AI regulation news...")
    
    start_btn = False
    if not st.session_state.session.is_active:
        start_btn = st.button("Start Interview", type="primary")
    else:
        if st.button("End Interview Early", type="secondary"):
            st.session_state.session.is_active = False
            st.rerun()

# Main Logic

def start_interview():
    if not startup_desc:
        st.error("Please enter a startup description.")
        return

    with st.spinner("Generating journalist persona and assets..."):
        # 1. Generate Assets
        outlet_name = generate_outlet_name(persona, startup_desc)
        j_img, l_img = generate_assets(persona, outlet_name)
        
        # 2. Initialize Session
        st.session_state.session.start_session(
            startup_desc, persona, difficulty, news_context, j_img, l_img
        )
        
        # 3. Initialize Agent
        st.session_state.journalist_agent = JournalistAgent(persona, difficulty, startup_desc, news_context)
        
        # 4. Generate First Question
        first_q = st.session_state.journalist_agent.generate_question([])
        st.session_state.session.set_current_question(first_q)
        
        st.rerun()

if start_btn:
    start_interview()

# View: Interview
if st.session_state.session.is_active:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.session_state.session.journalist_image:
            st.image(st.session_state.session.journalist_image, caption="Your Interviewer", width="stretch")
        if st.session_state.session.logo_image:
            st.image(st.session_state.session.logo_image, width=100)
            
    with col2:
        # Display History
        for i, turn in enumerate(st.session_state.session.transcript):
            with st.chat_message("assistant", avatar=st.session_state.session.journalist_image):
                st.write(turn['question'])
            with st.chat_message("user"):
                st.write(turn['answer'])

        # Display Current Question
        with st.chat_message("assistant", avatar=st.session_state.session.journalist_image):
            st.write(st.session_state.session.current_question)

        # Input for New Answer
        with st.chat_message("user"):
            audio_key = f"audio_{len(st.session_state.session.transcript)}"
            audio_value = st.audio_input("Record your answer", key=audio_key)
        
        if audio_value:
            with st.spinner("Transcribing and thinking..."):
                # 1. Transcribe
                audio_bytes = audio_value.read()
                transcript_text = transcribe_audio(audio_bytes)
                
                # 2. Add to history
                st.session_state.session.add_turn(st.session_state.session.current_question, transcript_text)
                
                # 3. Generate Next Question
                next_q = st.session_state.journalist_agent.generate_question(st.session_state.session.transcript)
                st.session_state.session.set_current_question(next_q)
                
                st.rerun()

# View: Evaluation (Post-Interview)
elif st.session_state.session.transcript:
    st.title("📊 Interview Evaluation")
    
    if not st.session_state.session.evaluation:
        with st.spinner("Analyzing your performance..."):
            evaluator = EvaluatorAgent()
            evaluation = evaluator.evaluate_interview(
                st.session_state.session.transcript,
                st.session_state.session.startup_description
            )
            st.session_state.session.evaluation = evaluation
    
    eval_data = st.session_state.session.evaluation
    
    if "error" in eval_data:
        st.error("Failed to generate evaluation.")
        st.write(eval_data)
    else:
        # Score
        score = eval_data.get('score', 0)
        st.metric("Overall Score", f"{score}/10")
        st.progress(score / 10)
        
        # Headline
        st.subheader(f"📰 {eval_data.get('headline', 'No Headline')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Strengths")
            for s in eval_data.get('strengths', []):
                st.success(s)
                
            st.markdown("### 💬 Best Quotes")
            for q in eval_data.get('quotes', []):
                st.info(f'"{q}"')

        with col2:
            st.markdown("### ⚠️ Weaknesses")
            for w in eval_data.get('weaknesses', []):
                st.warning(w)
                
            st.markdown("### 🚩 Risky Statements")
            for r in eval_data.get('risky_statements', []):
                st.error(f'"{r}"')

        st.markdown("### 🔄 Rewrites")
        for rewrite in eval_data.get('rewrites', []):
            with st.container(border=True):
                st.markdown(f"**Original:** {rewrite.get('original')}")
                st.markdown(f"**Better:** {rewrite.get('better')}")

        st.markdown("### 📅 7-Day Training Plan")
        for day in eval_data.get('training_plan', []):
            st.markdown(f"- {day}")
            
    if st.button("Start New Interview"):
        st.session_state.session = InterviewSession()
        st.rerun()

# View: Welcome Screen (Initial State)
else:
    st.title("Welcome to PressCoach")
    st.markdown("""
    Practice your high-stakes media interviews with an AI journalist.
    
    1. **Setup**: Enter your startup details and choose a journalist persona.
    2. **Interview**: Answer questions via voice. The AI listens and reacts.
    3. **Feedback**: Get a detailed PR evaluation and score.
    
    👈 **Start by filling out the sidebar.**
    """)
