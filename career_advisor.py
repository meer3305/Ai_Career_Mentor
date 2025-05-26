import streamlit as st
import pandas as pd
import spacy
from PyPDF2 import PdfReader
import docx
from collections import defaultdict

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Enhanced career database with salary ranges
TECH_CAREERS = {
    "Data Scientist": {
        "required_skills": ["python", "sql", "machine learning", "statistics", "data analysis", "pandas", "numpy"],
        "preferred_education": ["computer science", "mathematics", "statistics", "engineering", "physics"],
        "description": "Extracts insights from complex data using statistical and machine learning techniques.",
        "salary_range": "$95,000 - $165,000",
        "demand": "Very High"
    },
    "Software Engineer": {
        "required_skills": ["programming", "algorithms", "data structures", "software development", "testing", "debugging"],
        "preferred_education": ["computer science", "software engineering", "computer engineering"],
        "description": "Designs, develops, and maintains software systems and applications.",
        "salary_range": "$85,000 - $160,000",
        "demand": "Very High"
    },
    "DevOps Engineer": {
        "required_skills": ["cloud computing", "docker", "kubernetes", "ci/cd", "aws", "azure", "linux"],
        "preferred_education": ["computer science", "information technology"],
        "description": "Bridges development and operations to improve deployment and system reliability.",
        "salary_range": "$100,000 - $180,000",
        "demand": "High"
    },
    "UX/UI Designer": {
        "required_skills": ["user research", "wireframing", "prototyping", "figma", "adobe xd", "usability testing"],
        "preferred_education": ["design", "human-computer interaction", "psychology"],
        "description": "Creates user-centered digital experiences through research and design.",
        "salary_range": "$75,000 - $140,000",
        "demand": "High"
    },
    "Data Engineer": {
        "required_skills": ["python", "sql", "etl", "data pipelines", "apache spark", "hadoop"],
        "preferred_education": ["computer science", "engineering", "information systems"],
        "description": "Builds and maintains data infrastructure and pipelines for analytics.",
        "salary_range": "$90,000 - $155,000",
        "demand": "High"
    }
}

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_skills(text):
    doc = nlp(text.lower())
    skills = set()
    
    technical_terms = {
        'python', 'java', 'sql', 'javascript', 'c++', 'c#', 'html', 'css',
        'machine learning', 'deep learning', 'data analysis', 'data visualization',
        'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn',
        'aws', 'azure', 'google cloud', 'docker', 'kubernetes',
        'tableau', 'power bi', 'excel', 'spark', 'hadoop',
        'git', 'jenkins', 'ci/cd', 'agile', 'scrum'
    }
    
    for chunk in doc.noun_chunks:
        normalized = chunk.text.lower().strip()
        if normalized in technical_terms:
            skills.add(normalized)
    
    for term in technical_terms:
        if term in text.lower():
            skills.add(term)
    
    return sorted(skills)

def extract_education(text):
    doc = nlp(text)
    education = []
    
    degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'm.sc', 'b.sc', 'm.tech', 'b.tech', 'degree', 'diploma']
    education_keywords = ['university', 'college', 'institute', 'school']
    
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(degree in sent_text for degree in degree_keywords):
            education.append(sent.text.strip())
        elif any(edu in sent_text for edu in education_keywords):
            education.append(sent.text.strip())
    
    return education if education else ["Education information not specified"]

def extract_experience(text):
    doc = nlp(text)
    experience = []
    
    experience_keywords = ['experience', 'worked', 'job', 'position', 'role', 'employed']
    
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in experience_keywords):
            experience.append(sent.text.strip())
    
    return experience if experience else ["Work experience not detailed"]

def calculate_career_match(user_profile):
    career_scores = {}
    user_skills = set(skill.lower() for skill in user_profile['skills'])
    user_education = ' '.join(user_profile['education']).lower()
    
    for career, details in TECH_CAREERS.items():
        required_skills = set(details['required_skills'])
        skill_match = len(user_skills.intersection(required_skills)) / len(required_skills)
        
        edu_match = 0
        for edu in details['preferred_education']:
            if edu in user_education:
                edu_match = 0.3
                break
        
        exp_match = 0.2 if len(user_profile['experience']) > 0 else 0
        
        total_score = (skill_match * 0.5) + edu_match + exp_match
        career_scores[career] = min(total_score * 100, 100)
    
    return sorted(career_scores.items(), key=lambda x: x[1], reverse=True)

def display_career_recommendations(recommendations):
    st.subheader("🌟 Recommended Career Paths")
    
    for career, score in recommendations:
        # Create the expander with proper formatting
        with st.expander(f"{career} ({score:.1f}% Match | {TECH_CAREERS[career]['salary_range']})", 
                        expanded=True if career == recommendations[0][0] else False):
            
            # Create a styled container for the description
            st.markdown(
                f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                ">
                    <p style="font-size: 16px; margin-bottom: 5px;">
                        <strong>Description:</strong> {TECH_CAREERS[career]['description']}
                    </p>
                    <p style="font-size: 16px;">
                        <strong>Market Demand:</strong> 
                        <span style="color: {'#27ae60' if TECH_CAREERS[career]['demand'] in ['High','Very High'] else '#e74c3c'}">
                            {TECH_CAREERS[career]['demand']}
                        </span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Create two columns for skills and education
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔧 Key Skills Needed:**")
                for skill in TECH_CAREERS[career]['required_skills']:
                    st.write(f"- {skill.title()}")
            
            with col2:
                st.markdown("**🎓 Preferred Education:**")
                for edu in TECH_CAREERS[career]['preferred_education']:
                    st.write(f"- {edu.title()}")
            
            # Add a divider
            st.markdown("---")

def main():
    st.set_page_config(
        page_title="AI Career Path Advisor",
        page_icon="🚀",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        /* Main styles */
        .main {
            background-color: #f8f9fa;
        }
        h1 {
            color: #2c3e50;
            font-weight: 700;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #3498db;
            font-weight: 600;
        }
        
        /* Button styles */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* File uploader */
        .stFileUploader>div>div>div>div {
            border: 2px dashed #3498db;
            border-radius: 8px;
            padding: 20px;
            background-color: #f0f8ff;
        }
        
        /* Expander styles */
        .stExpander {
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            border-left: 5px solid #4CAF50;
        }
        .stExpander:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Progress bar */
        .stProgress>div>div>div {
            background-color: #4CAF50;
        }
        
        /* Input fields */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 8px;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="background-color:#4CAF50;padding:20px;border-radius:10px;margin-bottom:30px">
        <h1 style="color:white;text-align:center;">AI-Powered Career Path Advisor</h1>
        <p style="color:white;text-align:center;">Discover your ideal technical career based on your skills and experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;margin-bottom:30px">
            <h2>Navigation</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        - **Resume Analysis** 📄
        - **Career Recommendations** 💡
        - **Market Insights** 📊
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center">
            <p>Need help? Contact our career advisors</p>
            <p><strong>careersupport@example.com</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Resume Upload Section
    with st.container():
        st.header("📋 Resume Analysis")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)", 
            type=["pdf", "docx"],
            help="We'll analyze your skills, education, and experience automatically"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)
                
                st.session_state.user_profile = {
                    "skills": extract_skills(text),
                    "education": extract_education(text),
                    "experience": extract_experience(text)
                }
                
                st.success("✅ Resume parsed successfully! We've identified your key qualifications.")
                
                with st.expander("View extracted information", expanded=True):
                    st.subheader("🔍 Identified Skills")
                    st.write(", ".join(st.session_state.user_profile['skills']) or "No skills detected")
                    
                    st.subheader("🎓 Education Background")
                    for edu in st.session_state.user_profile['education']:
                        st.write(edu)
                    
                    st.subheader("💼 Work Experience")
                    for exp in st.session_state.user_profile['experience']:
                        st.write(exp)
            
            except Exception as e:
                st.error(f"⚠️ Error processing file: {str(e)}")
    
    # Career Recommendations Section
    if st.session_state.user_profile:
        with st.container():
            st.header("💡 Career Recommendations")
            recommendations = calculate_career_match(st.session_state.user_profile)
            display_career_recommendations(recommendations)
            
            # Top recommendation highlight
            top_career, top_score = recommendations[0]
            st.markdown(f"""
            <div style="background-color:#e8f5e9;padding:20px;border-radius:10px;margin-top:30px">
                <h3 style="color:#2c3e50;margin-top:0;">Your Best Match</h3>
                <h2 style="color:#4CAF50;margin-bottom:10px;">{top_career}</h2>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <p style="margin-bottom:5px;"><strong>Match Score:</strong> {top_score:.1f}%</p>
                        <p style="margin-bottom:5px;"><strong>Salary Range:</strong> {TECH_CAREERS[top_career]['salary_range']}</p>
                        <p><strong>Demand:</strong> {TECH_CAREERS[top_career]['demand']}</p>
                    </div>
                    <div style="width:60%;">
                        <div style="height:10px;background-color:#e0e0e0;border-radius:5px;overflow:hidden;">
                            <div style="height:100%;width:{top_score}%;background-color:#4CAF50;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Manual Input Fallback
    with st.expander("Don't have a resume? Enter your details manually", expanded=False):
        with st.form("manual_input"):
            manual_skills = st.text_input(
                "Your skills (comma separated)", 
                help="e.g., Python, SQL, Data Analysis"
            )
            manual_education = st.text_input(
                "Your highest degree", 
                help="e.g., B.Sc Computer Science"
            )
            manual_experience = st.text_area(
                "Your work experience", 
                help="Briefly describe your work experience"
            )
            
            if st.form_submit_button("Get Recommendations"):
                if manual_skills or manual_education:
                    st.session_state.user_profile = {
                        "skills": [s.strip() for s in manual_skills.split(",")] if manual_skills else [],
                        "education": [manual_education] if manual_education else [],
                        "experience": [manual_experience] if manual_experience else []
                    }
                    st.rerun()
                else:
                    st.warning("Please provide at least your skills or education")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;margin-top:50px;padding:20px;background-color:#f8f9fa;border-radius:8px">
        <p style="color:#7f8c8d;font-size:14px;">© 2023 Career Path Advisor. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()