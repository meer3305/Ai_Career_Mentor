def app():    
    import sys
    import os
    import json
    import base64
    from io import BytesIO
    from PIL import Image
    import streamlit as st
    from streamlit_extras.let_it_rain import rain

    # Add project root to sys.path
    def find_project_root(marker=".git"):
        """Find the project root by searching for a marker file or directory."""
        current_dir = os.path.abspath(os.path.dirname(__file__))
        while current_dir != os.path.dirname(current_dir):  # Stop at the filesystem root
            if marker in os.listdir(current_dir):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        raise FileNotFoundError(f"Could not find project root with marker '{marker}'")

    try:
        project_root = find_project_root()
        sys.path.append(project_root)
    except FileNotFoundError as e:
        st.error(f"Error locating project root: {e}")
        st.stop()

    # Import local modules
    try:
        from modules.interview_simulator import generate_mcq_general, generate_mcq_dsa
        from modules.utils import create_pdf
    except ImportError as e:
        st.error(f"Module import error: {e}")
        st.stop()

    # --- Page Configuration ---
    def main():
        """Main function to set up the Streamlit app."""
        st.set_page_config(
            page_title="🧠 Test your knowledge",
            layout="wide",
            initial_sidebar_state="expanded",
            page_icon="🎙️",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': "https://github.com/your-repo/issues",
                'About': "# AI Career Mentor - Interview Simulator"
            }
        )
   

    # --- Custom CSS ---
    def inject_custom_css():
        st.markdown("""
        <style>
            /* Main container */
            .stApp {
                background-color: #000; /* Black background */
                color: #ffe600; /* Yellow text */
            }
            
            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background: #000; /* Black background */
                color: #ffe600; /* Yellow text */
            }
            
            /* Button styling */
            .stButton>button {
                border-radius: 8px;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
                color: #000; /* Black text */
                background-color: #ffe600; /* Yellow background */
                border: 1px solid #0074d9; /* Blue border */
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                background-color: #0074d9; /* Blue background on hover */
                color: #ffe600; /* Yellow text on hover */
            }
            
            /* Question cards */
            .question-card {
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                background-color: #000; /* Black background */
                border-left: 4px solid #0074d9; /* Blue border */
                color: #ffe600 !important; /* Yellow text for visibility */
            }
            
            /* Feedback cards */
            .feedback-correct {
                background-color: #e5ffe5; /* Light green for correct */
                border-left: 4px solid #0074d9; /* Blue border */
                color: #000; /* Black text */
            }
            
            .feedback-incorrect {
                background-color: #ffe5e5; /* Light red for incorrect */
                border-left: 4px solid #ff4136; /* Red border */
                color: #000; /* Black text */
            }
            
            /* Progress bar */
            .stProgress > div > div > div {
                background-color: #0074d9; /* Blue progress bar */
            }
            
            /* Radio buttons */
            [data-baseweb="radio"] {
                margin-bottom: 0.5rem;
                color: #ffe600; /* Yellow text */
            }
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .stButton>button {
                    width: 100%;
                }
                .question-card {
                    padding: 1rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    inject_custom_css()

    # --- Session State Management ---
    def initialize_session_state():
        defaults = {
            'interview_started': False,
            'interview_complete': False,
            'current_round': 0,
            'score_history': [None]*10,
            'feedbacks': [None]*10,
            'mcq_answers': [None]*10,
            'answered_count': 0,
            'selected_role': None,
            'difficulty': "Medium",
            'keywords': ""
        }
        
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    initialize_session_state()

    # --- Helper Functions ---
    def load_roles():
        try:
            with open("config/job_roles.json") as f:
                data = json.load(f)
            return data.get("roles", [])
        except Exception:
            st.warning("Warning: 'config/job_roles.json' file is missing or corrupted. Using fallback roles.")
            return ["Software Engineer", "Data Scientist", "Product Manager"]

    def calculate_progress():
        total_questions = len(st.session_state.score_history)
        return st.session_state.answered_count / total_questions if total_questions > 0 else 0

    def display_question_card(question_num, question_data):
        """Display a question card with consistent styling"""
        st.markdown(
            f"""
            <div class="question-card">
                <h4 style="color: #ffe600;">Question {question_num}</h4>
                <p style="font-size: 1.05rem; color: #ffe600;">{question_data['question']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display code if present
        if question_data.get("code"):
            st.code(question_data["code"], language="python")
        
        # Display graph/image if present
        if question_data.get("graph"):
            try:
                if question_data["graph"].startswith("data:image"):
                    _, encoded = question_data["graph"].split(",", 1)
                    img_bytes = base64.b64decode(encoded)
                    img = Image.open(BytesIO(img_bytes))
                    st.image(img, use_column_width=True)
                else:
                    st.image(question_data["graph"], use_column_width=True)
            except Exception as e:
                st.warning(f"Couldn't display image: {str(e)}")

    def display_feedback(question_num, is_correct, correct_answer, explanation):
        """Display feedback with appropriate styling"""
        feedback_class = "feedback-correct" if is_correct else "feedback-incorrect"
        icon = "✅" if is_correct else "❌"
        color = "#000"
        
        st.markdown(
            f"""
            <div class="{feedback_class}" style="padding: 1rem; border-radius: 8px; margin-top: 1rem; color: #000;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem; color: {color};">{icon}</span>
                    <strong style="color: {color};">
                        {"Correct!" if is_correct else "Incorrect"}
                    </strong>
                </div>
                <p style="color: #000;"><strong>Correct Answer:</strong> {correct_answer}</p>
                <p style="color: #000;"><em>{explanation}</em></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Sidebar ---
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")

        # Role or custom keyword selection
        role_mode = st.radio(
            "Choose Question Source",
            ["Select Role", "Custom Keywords"],
            index=0,
            key="sidebar_role_mode"
        )

        roles = load_roles()

        if role_mode == "Select Role":
            st.session_state.selected_role = st.selectbox(
                "🎯 Select Role",
                roles,
                index=roles.index(st.session_state.selected_role) if st.session_state.selected_role in roles else 0,
                key="sidebar_role"
            )
            st.session_state.keywords = ""
        else:
            st.session_state.selected_role = None
            st.session_state.keywords = st.text_input(
                "🔑 Custom Keywords (comma separated)",
                value=st.session_state.keywords,
                key="sidebar_keywords",
                help="Add specific topics you want to focus on"
            )

        # Difficulty selection
        st.session_state.difficulty = st.selectbox(
            "⚡ Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
            key="sidebar_difficulty"
        )

        st.markdown("---")

        # Progress tracking
        progress = calculate_progress()
        st.progress(progress)
        st.caption(f"Completed: {int(progress * 10)}/10 questions")

        st.markdown("---")

        # Help section
        st.subheader("💡 Tips for Success")
        st.markdown("""
            - Read each question carefully
            - Manage your time effectively
            - Review explanations for all answers
            - Practice regularly to improve
        """)

    # --- Main Content ---
    st.title("🧠 Time to Test Your Knowledge ")
    st.markdown("""
        <div style="background: linear-gradient(90deg, #000000, #6d28d9, #2563eb);
                    color: #fff; padding: 1.5rem; border-radius: 12px; 
                    margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h2 style="color: #fff; margin-bottom: 0.5rem;">Practice Makes Perfect</h2>
            <p style="margin-bottom: 0; opacity: 0.9;">
                Get to know how good you are with your knowledge and get instant feedback on your performance.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- Interview Flow Control ---
    if not st.session_state.interview_started:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### Ready to test your skills?")
            if st.button("🚀 Launch Test", use_container_width=True, type="primary"):
                st.session_state.interview_started = True
                st.session_state.interview_complete = False
                st.session_state.current_round = 1
                st.session_state.score_history = [None]*10
                st.session_state.feedbacks = [None]*10
                st.session_state.mcq_answers = [None]*10
                st.session_state.answered_count = 0
                st.rerun()

    elif st.session_state.interview_started and not st.session_state.interview_complete:
        # Round 1: General Knowledge (Q1-Q5)
        if st.session_state.current_round == 1:
            st.markdown("## 📚 Round 1: General Knowledge")
            st.markdown("Test your fundamental concepts with these 5 questions.")
            st.markdown("---")
            
            all_submitted = True
            for i in range(5):
                mcq_key = f"mcq{i+1}"
                submitted_key = f"mcq_submitted_{i+1}"
                
                # Generate question if not exists
                if mcq_key not in st.session_state:
                    with st.spinner(f"Generating question {i+1}..."):
                        try:
                            st.session_state[mcq_key] = generate_mcq_general(
                                st.session_state.selected_role,
                                st.session_state.difficulty,
                                [k.strip() for k in st.session_state.keywords.split(",")] if st.session_state.keywords else None
                            )
                        except Exception as e:
                            st.session_state[mcq_key] = {"error": str(e)}
                            st.error(f"Error generating question {i+1}: {str(e)}")

                if submitted_key not in st.session_state:
                    st.session_state[submitted_key] = False
                
                mcq = st.session_state[mcq_key]
                
                # Error handling
                if "error" in mcq:
                    st.error(f"Error generating question {i+1}: {mcq['error']}")
                    continue
                
                # Display question
                display_question_card(i+1, mcq)
                
                # Answer selection
                cols = st.columns([4, 1])
                with cols[0]:
                    answer = st.radio(
                        f"Select answer for Q{i+1}",
                        mcq["options"],
                        key=f"mcq_ans_{i+1}",
                        index=0,
                        label_visibility="collapsed"
                    )
                
                # Submit button
                with cols[1]:
                    if st.button(f"Submit", key=f"submit_mcq_{i+1}", 
                            disabled=st.session_state[submitted_key]):
                        st.session_state[submitted_key] = True
                        st.session_state.mcq_answers[i] = answer
                        is_correct = answer == mcq["correct_answer"]
                        st.session_state[f"mcq_correct_{i+1}"] = is_correct
                        st.session_state.score_history[i] = 10 if is_correct else 0
                        st.session_state.feedbacks[i] = mcq["explanation"]
                        st.session_state.answered_count += 1
                        st.rerun()
                
                # Show feedback if submitted
                if st.session_state[submitted_key]:
                    display_feedback(
                        i+1,
                        st.session_state[f"mcq_correct_{i+1}"],
                        mcq["correct_answer"],
                        mcq["explanation"]
                    )
                else:
                    all_submitted = False
            
            # Proceed to next round if all submitted
            if all_submitted:
                st.markdown("---")
                if st.button("➡️ Continue to DSA Questions", type="primary"):
                    st.session_state.current_round = 2
                    st.rerun()

        # Round 2: DSA Questions (Q6-Q10)
        elif st.session_state.current_round == 2:
            st.markdown("## 💻 Round 2: Data Structures & Algorithms")
            st.markdown("Test your problem-solving skills with these 5 DSA questions.")
            st.markdown("---")
            
            all_submitted = True
            for i in range(5, 10):
                mcq_key = f"mcq{i+1}"
                submitted_key = f"mcq_submitted_{i+1}"
                
                # Generate question if not exists
                if mcq_key not in st.session_state:
                    with st.spinner(f"Generating question {i+1}..."):
                        try:
                            st.session_state[mcq_key] = generate_mcq_dsa(
                                st.session_state.selected_role,
                                st.session_state.difficulty,
                                [k.strip() for k in st.session_state.keywords.split(",")] if st.session_state.keywords else None
                            )
                        except Exception as e:
                            st.session_state[mcq_key] = {"error": f"Failed to generate question: {str(e)}"}
                
                if submitted_key not in st.session_state:
                    st.session_state[submitted_key] = False
                
                mcq = st.session_state[mcq_key]
                
                # Error handling
                if "error" in mcq:
                    st.error(f"Error generating question {i+1}: {mcq['error']}")
                    continue
                
                # Display question
                display_question_card(i+1, mcq)
                
                # Answer selection
                cols = st.columns([4, 1])
                with cols[0]:
                    answer = st.radio(
                        f"Select answer for Q{i+1}",
                        mcq["options"],
                        key=f"mcq_ans_{i+1}",
                        index=0,
                        label_visibility="collapsed"
                    )
                
                # Submit button
                with cols[1]:
                    if st.button(f"Submit", key=f"submit_mcq_{i+1}", 
                            disabled=st.session_state[submitted_key]):
                        st.session_state[submitted_key] = True
                        st.session_state.mcq_answers[i] = answer
                        is_correct = answer == mcq["correct_answer"]
                        st.session_state[f"mcq_correct_{i+1}"] = is_correct
                        st.session_state.score_history[i] = 10 if is_correct else 0
                        st.session_state.feedbacks[i] = mcq["explanation"]
                        st.session_state.answered_count += 1
                        st.rerun()
                
                # Show feedback if submitted
                if st.session_state[submitted_key]:
                    display_feedback(
                        i+1,
                        st.session_state[f"mcq_correct_{i+1}"],
                        mcq["correct_answer"],
                        mcq["explanation"]
                    )
                else:
                    all_submitted = False
            
            # Complete interview if all submitted
            if all_submitted:
                st.session_state.interview_complete = True
                st.rerun()

    # --- Results Page ---
    elif st.session_state.interview_complete:
        st.markdown("## 🎉 Test Completed!")
        
        # Calculate scores
        total_score = sum(s for s in st.session_state.score_history if s is not None)
        max_score = 100
        percentage = (total_score / max_score) * 100
        
        # Score summary card
        with st.container():
            st.markdown("""
            <div style="background: #000; border-radius: 12px; padding: 1.5rem; 
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 2rem; color: #fff;">
                <h3 style="color: #a259ff; margin-bottom: 1rem;">📊 Your Score</h3>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 style="margin: 0; color: #fff;">{}/100</h1>
                        <p style="margin: 0; color: #fff;">{:.1f}% Correct</p>
                    </div>
                    <div style="width: 100px; height: 100px;">
                        <div data-testid="stProgress" style="width: 100%; height: 100%;">
                            <div role="progressbar" style="transform: rotate(-90deg);">
                                <svg viewBox="0 0 100 100" style="display: block;">
                                    <circle cx="50" cy="50" r="45" fill="none" stroke="#fff" 
                                            stroke-width="10"></circle>
                                    <circle cx="50" cy="50" r="45" fill="none" stroke="#a259ff" 
                                            stroke-width="10" stroke-dasharray="{} 283">
                                    </circle>
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """.format(total_score, percentage, 2.83 * percentage), 
            unsafe_allow_html=True)
        
        # Detailed feedback
        st.markdown("### 📝 Question Feedback")
        for i in range(10):
            if st.session_state.feedbacks[i] is not None:
                with st.expander(f"Question {i+1} - {'✅ Correct' if st.session_state.score_history[i] == 10 else '❌ Incorrect'}"):
                    st.markdown(f"**Your Answer:** {st.session_state.mcq_answers[i]}")
                    st.markdown(f"**Feedback:** {st.session_state.feedbacks[i]}")
        
        # Celebration effect
        rain(emoji="✨", font_size=30, falling_speed=5, animation_length=1)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                summary = {
                    "Role": st.session_state.selected_role,
                    "Difficulty": st.session_state.difficulty,
                    "Score": f"{total_score}/100",
                    "Percentage": f"{percentage:.1f}%",
                    "Feedbacks": [
                        f"Q{i+1}: {fb}" 
                        for i, fb in enumerate(st.session_state.feedbacks) 
                        if fb is not None
                    ],
                    "Answers": [
                        f"Q{i+1}: {ans}" 
                        for i, ans in enumerate(st.session_state.mcq_answers) 
                        if ans is not None
                    ]
                }
                
                try:
                    pdf_path = create_pdf(summary, filename="Interview_Report.pdf")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Full Report",
                            data=f,
                            file_name="Interview_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error generating PDF report: {e}")
                    st.markdown("### 📄 Alternative Report")
                    st.text("Role: " + summary["Role"])
                    st.text("Difficulty: " + summary["Difficulty"])
                    st.text("Score: " + summary["Score"])
                    st.text("Percentage: " + summary["Percentage"])
                    st.text("Feedbacks:")
                    for feedback in summary["Feedbacks"]:
                        st.text(feedback)
                    st.text("Answers:")
                    for answer in summary["Answers"]:
                        st.text(answer)
        
        with col2:
            if st.button("🔄 Start New Test", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()