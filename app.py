import frontend.pages.resume_analysis_app as resume_analysis
import frontend.pages.skill_gap_app as skill_gap
import frontend.pages.career_advisor_app as career_advisor
import frontend.pages.roadmap_Generator_app as roadmap
import frontend.pages.job_scrapping_app as job_scraper
import frontend.pages.interview_simulator_app as interview_simulator

import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add frontend/pages to the system path for import
sys.path.append(os.path.abspath("frontend/pages"))

# Set Streamlit page config with modern theme
st.set_page_config(
    page_title="AI Career Mentor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .sidebar .sidebar-content {
        background-color: #1a1a2e;
    }
    .css-1d391kg, .st-b7, .st-b8, .st-b9 {
        color: #ffffff;
    }
    .css-1aumxhk {
        background-color: #16213E;
        color: white;
    }
    .st-bb {
        background-color: transparent;
    }
    .st-at {
        background-color: #1a1a2e;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #4CC9F0 !important;
    }
    .css-10trblm {
        color: #4CC9F0;
    }
    .st-cm {
        color: #F72585;
    }
    .st-fq {
        color: #B5179E;
    }
    .stButton>button {
        background-color: #4CC9F0;
        color: #0E1117;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3AA8D8;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation with custom menu
with st.sidebar:
    st.markdown("# 🧠 AI Career Mentor")
    st.markdown("""
    <div style="color: #a1a1a1; font-size: 14px; margin-bottom: 20px;">
    Your intelligent career development assistant powered by AI
    </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["🏠 Home", "📄 Resume Analyzer", "🧠 Skill Gap Detector", 
                "💬 Career Advisor", "🗺️ Roadmap Generator", 
                "💼 Job Finder", "🧠 Knowledge Check"],
        icons=["house", "file-text", "brain", "chat-left-text", "map", 
               "briefcase", "brain"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#1a1a2e"},
            "icon": {"color": "#4CC9F0", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#16213E"},
            "nav-link-selected": {"background-color": "#4CC9F0", "color": "#0E1117", "font-weight": "bold"},
        }
    )

# Home Page
if selected == "🏠 Home":
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        # 🧠 Welcome to AI Career Mentor
        
        <div style="color: #a1a1a1; font-size: 16px; margin-bottom: 30px;">
        Your comprehensive AI-powered career development platform designed to help you 
        analyze, improve, and navigate your professional journey with cutting-edge 
        artificial intelligence.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### ✨ Key Features:
        
        - **📄 Resume Analyzer**: Get instant feedback on your resume with AI-powered analysis
        - **🧠 Skill Gap Detector**: Identify missing skills for your dream job
        - **💬 Career Advisor**: Personalized career guidance based on your profile
        - **🗺️ Roadmap Generator**: Create customized learning paths for career growth
        - **💼 Job Finder**: Discover relevant job opportunities with smart matching
        - **🧠 Knowledge Check**: Test your knowledge with AI-powered feedback
        
        <div style="margin-top: 30px; color: #4CC9F0; font-size: 14px;">
        Select a feature from the sidebar to get started on your career development journey!
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3281/3281289.png", 
                width=300, caption="AI Career Development Assistant")
        
    st.markdown("---")
    
    st.markdown("""
    ### 🚀 How It Works:
    
    1. **Upload your resume** or enter your career details
    2. **Select the service** you need from our AI-powered tools
    3. **Get instant insights** and actionable recommendations
    4. **Implement the suggestions** and track your career growth
    
    <div style="margin-top: 20px; color: #a1a1a1; font-size: 14px;">
    Our platform uses advanced natural language processing and machine learning algorithms 
    to provide you with the most accurate and personalized career advice.
    </div>
    """, unsafe_allow_html=True)

# Render selected page
elif selected == "📄 Resume Analyzer":
    resume_analysis.app()

elif selected == "🧠 Skill Gap Detector":
    skill_gap.app()

elif selected == "💬 Career Advisor":
    career_advisor.app()

elif selected == "🗺️ Roadmap Generator":
    roadmap.app()

elif selected == "💼 Job Finder":
    job_scraper.app()  

elif selected == "🧠 Knowledge Check":
    interview_simulator.app()