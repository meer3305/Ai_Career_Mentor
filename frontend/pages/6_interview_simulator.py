import streamlit as st
import json
from modules.interview_simulator import *
from modules.utils import create_pdf
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain

# Page Config
st.set_page_config(
    page_title="🧠 AI Interview Simulator", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎙️"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .stSelectbox, .stTextInput, .stButton>button {
            border-radius: 10px !important;
        }
        .stButton>button {
            background-color: #4f46e5 !important;
            color: white !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #4338ca !important;
            transform: scale(1.05);
        }
        .question-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .feedback-card {
            background: #f0f9ff;
            border-left: 5px solid #4f46e5;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .header-accent {
            background: linear-gradient(90deg, #4f46e5, #8b5cf6);
            color: white;
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .score-display {
            font-size: 1.2rem;
            font-weight: bold;
            color: #4f46e5;
        }
        .progress-bar {
            height: 10px;
            background: #e0e7ff;
            border-radius: 5px;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f46e5, #8b5cf6);
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=AI+Interviewer", width=150)
    st.title("Settings")
    st.markdown("---")
    
    # Load roles
    with open("config/job_roles.json", "r") as f:
        roles = json.load(f)
    
    selected_role = st.selectbox("🎯 Select a Role", roles)
    difficulty = st.selectbox("⚙️ Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    keywords = st.text_input("🔑 Custom Keywords (comma-separated)")
    
    st.markdown("---")
    st.markdown("### Interview Progress")
    progress_bar = st.progress(0)
    st.markdown("---")
    st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Groq](https://groq.com/)")

# Main Content
st.title("🧠 AI-Powered Interview Simulator")
st.markdown("""
    <div class="header-accent">
        Get ready for your dream job! Practice with our AI interviewer and receive instant feedback.
    </div>
""", unsafe_allow_html=True)

if st.button("🚀 Launch Interview", use_container_width=True):
    rain(emoji="✨", font_size=20, falling_speed=5, animation_length=1)
    st.session_state.interview_started = True
    st.session_state.current_round = 1
    st.session_state.score_history = []
    st.session_state.feedbacks = []
    st.session_state.answers = []
    st.session_state.mcq_answers = [None] * 3
    st.session_state.fill_answer = None
    st.session_state.dsa_answer = None

if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False

if st.session_state.interview_started:
    # Progress tracking
    total_questions = 5  # 3 MCQs + 1 Fill + 1 DSA
    completed_questions = sum(1 for ans in st.session_state.mcq_answers if ans is not None)
    completed_questions += 1 if st.session_state.fill_answer else 0
    progress = completed_questions / total_questions
    progress_bar.progress(progress)
    
    # Round 1: MCQs
    if st.session_state.current_round == 1:
        st.markdown(f"<h2 style='color: #4f46e5;'>📘 Round 1: Multiple Choice Questions</h2>", unsafe_allow_html=True)
        st.markdown("*Answer 3 questions to test your fundamental knowledge*")
        
        for i in range(3):
            if f"mcq{i+1}" not in st.session_state:
                st.session_state[f"mcq{i+1}"] = generate_mcq(
                    selected_role, 
                    difficulty, 
                    keywords.split(",") if keywords else None
                )
            
            with st.container():
                with stylable_container(
                    key=f"question_{i+1}",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 15px;
                            padding: calc(1em - 1px);
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        }
                    """,
                ):
                    st.markdown(f"**Question {i+1}:**\n\n{st.session_state[f'mcq{i+1}']}")
                    cols = st.columns([3,1])
                    with cols[0]:
                        st.session_state.mcq_answers[i] = st.radio(
                            f"Select your answer for Q{i+1}",
                            ["A", "B", "C", "D"],
                            key=f"mcq_ans_{i+1}",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                    with cols[1]:
                        if st.button(f"Submit Q{i+1}", key=f"submit_mcq_{i+1}"):
                            fb = evaluate_answer(st.session_state.mcq_answers[i], selected_role, difficulty)
                            st.session_state.feedbacks.append(fb)
                            score_line = [line for line in fb.splitlines() if "score" in line.lower()]
                            score = int(''.join(filter(str.isdigit, score_line[0]))) if score_line else 5
                            st.session_state.score_history.append(score)
                            
                            with st.expander(f"Feedback for Q{i+1}"):
                                st.markdown(f"""
                                    <div class="feedback-card">
                                        {fb}
                                    </div>
                                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        if all(ans is not None for ans in st.session_state.mcq_answers):
            if st.button("➡️ Proceed to Round 2", use_container_width=True):
                st.session_state.current_round = 2
                st.rerun()
    
    # Round 2: Fill in the Blank
    if st.session_state.current_round == 2:
        st.markdown(f"<h2 style='color: #4f46e5;'>✍️ Round 2: Fill in the Blank</h2>", unsafe_allow_html=True)
        st.markdown("*Test your practical knowledge with this scenario-based question*")
        
        if "fill_q" not in st.session_state:
            st.session_state.fill_q = generate_fill_in(selected_role, difficulty)
        
        with st.container():
            with stylable_container(
                key="fill_container",
                css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 15px;
                        padding: calc(1em - 1px);
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }
                """,
            ):
                st.markdown(f"**Question:**\n\n{st.session_state.fill_q}")
                st.session_state.fill_answer = st.text_area(
                    "Type your answer here...",
                    key="fill_ans",
                    height=150
                )
                
                if st.button("Submit Answer", key="submit_fill"):
                    fb = evaluate_answer(st.session_state.fill_answer, selected_role, difficulty)
                    st.session_state.feedbacks.append(fb)
                    score_line = [line for line in fb.splitlines() if "score" in line.lower()]
                    score = int(''.join(filter(str.isdigit, score_line[0]))) if score_line else 5
                    st.session_state.score_history.append(score)
                    
                    with st.expander("Feedback"):
                        st.markdown(f"""
                            <div class="feedback-card">
                                {fb}
                            </div>
                        """, unsafe_allow_html=True)
        
        if st.session_state.fill_answer:
            if st.button("➡️ Proceed to Final Round", use_container_width=True):
                st.session_state.current_round = 3
                st.rerun()
    
    # Round 3: DSA/Logic Challenge
    if st.session_state.current_round == 3:
        st.markdown(f"<h2 style='color: #4f46e5;'>🧩 Round 3: Logic Challenge</h2>", unsafe_allow_html=True)
        st.markdown("*Solve this problem to demonstrate your problem-solving skills*")
        
        if "dsa_q" not in st.session_state:
            st.session_state.dsa_q = generate_dsa_puzzle(selected_role)
        
        with st.container():
            with stylable_container(
                key="dsa_container",
                css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 15px;
                        padding: calc(1em - 1px);
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }
                """,
            ):
                st.markdown(f"**Challenge:**\n\n{st.session_state.dsa_q}")
                st.session_state.dsa_answer = st.text_area(
                    "Explain your approach and solution...",
                    key="dsa_ans",
                    height=200
                )
                
                if st.button("Submit Solution", key="submit_dsa"):
                    fb = evaluate_answer(st.session_state.dsa_answer, selected_role, difficulty)
                    st.session_state.feedbacks.append(fb)
                    score_line = [line for line in fb.splitlines() if "score" in line.lower()]
                    score = int(''.join(filter(str.isdigit, score_line[0]))) if score_line else 5
                    st.session_state.score_history.append(score)
                    
                    with st.expander("Feedback"):
                        st.markdown(f"""
                            <div class="feedback-card">
                                {fb}
                            </div>
                        """, unsafe_allow_html=True)
        
        if st.session_state.dsa_answer:
            if st.button("🏁 Complete Interview", use_container_width=True):
                st.session_state.interview_complete = True
                st.rerun()
    
    # Interview Completion
    if 'interview_complete' in st.session_state and st.session_state.interview_complete:
        st.balloons()
        st.markdown(f"<h2 style='color: #4f46e5; text-align: center;'>🎉 Interview Complete!</h2>", unsafe_allow_html=True)
        
        avg_score = sum(st.session_state.score_history)/len(st.session_state.score_history) if st.session_state.score_history else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with stylable_container(
                key="score_card",
                css_styles="""
                    {
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                """,
            ):
                st.metric("Average Score", f"{avg_score:.1f}/10")
        with col2:
            with stylable_container(
                key="difficulty_card",
                css_styles="""
                    {
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                """,
            ):
                st.metric("Difficulty Level", difficulty)
        with col3:
            with stylable_container(
                key="role_card",
                css_styles="""
                    {
                        background: white;
                        border-radius: 15px;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                """,
            ):
                st.metric("Job Role", selected_role)
        
        st.markdown("### Detailed Feedback")
        for i, fb in enumerate(st.session_state.feedbacks):
            with st.expander(f"Question {i+1} Feedback"):
                st.markdown(f"""
                    <div class="feedback-card">
                        {fb}
                    </div>
                """, unsafe_allow_html=True)
        
        # Generate PDF Report
        if st.button("📄 Generate Comprehensive Report", use_container_width=True):
            summary = {
                "Role": selected_role,
                "Difficulty": difficulty,
                "Scores": str(st.session_state.score_history),
                "Average Score": f"{avg_score:.2f}",
                "Feedback Summary": "\n\n".join(st.session_state.feedbacks)
            }
            filename = create_pdf(summary)
            
            with open(filename, "rb") as f:
                st.download_button(
                    "📥 Download Full Report as PDF", 
                    f, 
                    file_name=f"Interview_Report_{selected_role.replace(' ', '_')}.pdf",
                    use_container_width=True
                )
        
        if st.button("🔄 Start New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()