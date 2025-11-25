import streamlit as st

try:
    import os
    from dotenv import load_dotenv
    from stt import transcribe_audio
    from interview_agents import JournalistAgent, EvaluatorAgent, generate_interviewer_details
    from interview_engine import InterviewSession
except Exception as e:
    st.error(f"CRITICAL ERROR: Failed to import modules. Details: {e}")
    st.stop()

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="PressCoach (beta)",
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
    st.title("🎙️ PressCoach (beta)")
    
    st.info(
        """**Privacy & AI Notice**
        
• No data is stored after your session.
• Download your results anytime.
• Powered by Google Gemini."""
    )

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
            st.session_state.session.save_transcript()
            st.session_state.session.is_active = False
            st.rerun()

# Main Logic

def start_interview():
    if not startup_desc:
        st.error("Please enter a startup description.")
        return

    with st.spinner("Generating journalist persona..."):
        # 1. Generate Details
        details = generate_interviewer_details(persona, startup_desc)
        j_name = details.get("name", "Alex P. Keats")
        outlet = details.get("outlet", "The Daily Tech")
        
        # 2. Initialize Session
        st.session_state.session.start_session(
            startup_desc, persona, difficulty, news_context, j_name, outlet
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
        st.info(f"**Journalist:** {st.session_state.session.journalist_name}")
        st.success(f"**Media:** {st.session_state.session.outlet_name}")
            
    with col2:
        # Display History
        for i, turn in enumerate(st.session_state.session.transcript):
            with st.chat_message("assistant"):
                st.write(turn['question'])
            with st.chat_message("user"):
                st.write(turn['answer'])

        # Display Current Question
        if st.session_state.session.current_question:
            with st.chat_message("assistant"):
                st.write(st.session_state.session.current_question)

        # Handle Question Generation (if waiting)
        if st.session_state.get("generating_next_q", False):
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    next_q = st.session_state.journalist_agent.generate_question(st.session_state.session.transcript)
                    st.session_state.session.set_current_question(next_q)
                    st.session_state["generating_next_q"] = False
                    st.rerun()

        # Input for New Answer (only if not generating)
        if not st.session_state.get("generating_next_q", False):
            with st.chat_message("user"):
                audio_key = f"audio_{len(st.session_state.session.transcript)}"
                audio_value = st.audio_input("Record your answer", key=audio_key)
            
            if audio_value:
                with st.spinner("Transcribing..."):
                    # 1. Transcribe
                    audio_bytes = audio_value.read()
                    transcript_text = transcribe_audio(audio_bytes)
                    
                    # 2. Add to history
                    st.session_state.session.add_turn(st.session_state.session.current_question, transcript_text)
                    st.session_state.session.current_question = None # Clear current question as it's now in history
                    
                    # 3. Trigger Next Question Generation
                    st.session_state["generating_next_q"] = True
                    
                    st.rerun()

# View: Evaluation (Post-Interview)
elif st.session_state.session.transcript:
    st.title("📊 Interview Evaluation")
    
    if not st.session_state.session.evaluation:
        with st.spinner("Analyzing your performance..."):
            evaluator = EvaluatorAgent()
            evaluation = evaluator.evaluate_interview(
                st.session_state.session.transcript,
                st.session_state.session.startup_description,
                st.session_state.session.difficulty
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
            
        # Generate Report Text
        report_text = f"""INTERVIEW REPORT
================

SETTINGS
--------
Startup Description: {st.session_state.session.startup_description}
Journalist Persona: {st.session_state.session.persona}
Difficulty: {st.session_state.session.difficulty}
News Context: {st.session_state.session.news_context}

EVALUATION
----------
Score: {score}/10
Headline: {eval_data.get('headline', 'N/A')}

Strengths:
{chr(10).join(['- ' + s for s in eval_data.get('strengths', [])])}

Weaknesses:
{chr(10).join(['- ' + w for w in eval_data.get('weaknesses', [])])}

Best Quotes:
{chr(10).join(['- "' + q + '"' for q in eval_data.get('quotes', [])])}

Risky Statements:
{chr(10).join(['- "' + r + '"' for r in eval_data.get('risky_statements', [])])}

Rewrites:
{chr(10).join([f"- Original: {r.get('original')}{chr(10)}  Better: {r.get('better')}" for r in eval_data.get('rewrites', [])])}

Training Plan:
{chr(10).join(['- ' + t for t in eval_data.get('training_plan', [])])}

TRANSCRIPT
----------
"""
        for i, turn in enumerate(st.session_state.session.transcript):
            report_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {turn['answer']}\n\n"

        st.download_button(
            label="📥 Download Full Report",
            data=report_text,
            file_name="interview_report.txt",
            mime="text/plain"
        )
            
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
