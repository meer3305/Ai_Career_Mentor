import streamlit as st
import spacy
from PyPDF2 import PdfReader
import docx
import json

def load_career_data(file_path="config/career_data.json"):
    """Loads career profiles and skills from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure 'config/career_data.json' exists.")
        st.stop()
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON from '{file_path}'. Please check the file format for errors.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred loading career profiles: {e}")
        st.stop()
    return {}

def app():
    # Alternative to st.set_page_config: display a custom header and favicon using HTML
    st.markdown(
        """
        <head>
            <title>AI Career Path Advisor</title>
            <link rel="icon" href="https://em-content.zobj.net/source/microsoft-teams/363/rocket_1f680.png">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        """,
        unsafe_allow_html=True
    )

    # Load NLP model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        st.error("Please download the English language model first by running: python -m spacy download en_core_web_sm")
        st.stop()

    # Load career data
    TECH_CAREERS = load_career_data()

    def extract_text_from_pdf(pdf_file):
        text = ""
        try:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
        return text

    def extract_text_from_docx(docx_file):
        try:
            doc = docx.Document(docx_file)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""

    def extract_skills(text):
        if not text:
            return []
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
        if not text:
            return ["Education information not specified"]
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
        if not text:
            return ["Work experience not detailed"]
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
            required_skills = set(skill.lower() for skill in details['required_skills'])
            skill_match = len(user_skills.intersection(required_skills)) / len(required_skills) if required_skills else 0
            
            edu_match = 0
            for edu in details['preferred_education']:
                if edu.lower() in user_education:
                    edu_match = 0.3
                    break
            
            exp_match = 0.2 if len(user_profile['experience']) > 0 and user_profile['experience'][0] != "Work experience not detailed" else 0
            
            total_score = (skill_match * 0.5) + edu_match + exp_match
            career_scores[career] = min(max(total_score * 100, 0), 100)  # Ensure score is between 0-100
            
        return sorted(career_scores.items(), key=lambda x: x[1], reverse=True)

    def display_career_recommendations(recommendations, TECH_CAREERS):
        st.markdown("""
            <div style="margin-bottom: 25px;">
                <h2 style="color:#38b6ff; font-weight:800; text-align:left; margin-bottom:0;">
                    🌟 Recommended Career Paths
                </h2>
                <p style="color:#e0e0e0; font-size:17px; margin-top:4px;">
                    Explore your best-fit roles based on your profile
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        for idx, (career, score) in enumerate(recommendations):
            is_top = idx == 0
            
            # Plain text label for the expander (no HTML)
            expander_label = f"{career} ({score:.1f}% Match | {TECH_CAREERS[career]['salary_range']})"
            
            with st.expander(expander_label, expanded=is_top):
                st.markdown(
                    f"""
                    <div style="
                        background: #2a2a2a;
                        padding: 18px 20px 12px 20px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                        border-left: 4px solid {'#4CAF50' if is_top else '#38b6ff'};
                    ">
                        <p style="font-size: 16px; margin-bottom: 8px; color: #e0e0e0;">
                            <strong>Description:</strong> {TECH_CAREERS[career]['description']}
                        </p>
                        <p style="font-size: 16px; margin-bottom: 8px; color: #e0e0e0;">
                            <strong>Market Demand:</strong> 
                            <span style="color: {'#27ae60' if TECH_CAREERS[career]['demand'] in ['High','Very High'] else '#e74c3c'}; font-weight:600;">
                                {TECH_CAREERS[career]['demand']}
                            </span>
                        </p>
                        <div style="margin-top:10px;">
                            <div style="height:12px;background-color:#444;border-radius:6px;overflow:hidden;">
                                <div style="height:100%;width:{score}%;background:linear-gradient(90deg,{'#4CAF50' if is_top else '#38b6ff'},#38b6ff);" title="Match Score"></div>
                            </div>
                            <p style="font-size:13px;color:#38b6ff;margin-top:2px;">
                                Match Score: <b>{score:.1f}%</b>
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("<span style='font-weight:700;font-size:16px;color:#e0e0e0;'>🔧 Key Skills Needed:</span>", unsafe_allow_html=True)
                st.markdown(
                    "<ul style='margin-top:6px;margin-bottom:0;'>"
                    + "".join([f"<li style='font-size:15px;color:#e0e0e0;'>{skill.title()}</li>" for skill in TECH_CAREERS[career]['required_skills']])
                    + "</ul>",
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown("<span style='font-weight:700;font-size:16px;color:#e0e0e0;'>🎓 Preferred Education:</span>", unsafe_allow_html=True)
                st.markdown(
                    "<ul style='margin-top:6px;margin-bottom:0;'>"
                    + "".join([f"<li style='font-size:15px;color:#e0e0e0;'>{edu.title()}</li>" for edu in TECH_CAREERS[career]['preferred_education']])
                    + "</ul>",
                    unsafe_allow_html=True
                )
            
            st.markdown(
                "<hr style='border:0;border-top:1.5px solid #444;margin:18px 0 0 0;'>",
                unsafe_allow_html=True
            )


    # Dark theme CSS
    st.markdown("""
        <style>
            :root {
                --primary: #38b6ff;
                --secondary: #4CAF50;
                --background: #121212;
                --surface: #1e1e1e;
                --text-primary: #e0e0e0;
                --text-secondary: #b0b0b0;
                --error: #e74c3c;
                --success: #27ae60;
            }
            
            html, body, .main {
                background: var(--background) !important;
                color: var(--text-primary) !important;
                font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: var(--primary) !important;
                font-weight: 700;
            }
            
            p, li, div, span {
                color: var(--text-primary) !important;
            }
            
            .stTextInput>div>div>input, .stTextArea>div>div>textarea {
                background-color: var(--surface) !important;
                border: 2px solid var(--primary) !important;
                border-radius: 8px !important;
                color: var(--text-primary) !important;
                padding: 8px 12px !important;
            }
            
            .stButton>button {
                background: linear-gradient(90deg, var(--primary), #0096FF) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 10px 24px !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(56, 182, 255, 0.3) !important;
            }
            
            .stFileUploader>div>div>div>div {
                background-color: var(--surface) !important;
                border: 2px dashed var(--primary) !important;
                border-radius: 10px !important;
            }
            
            .stExpander {
                background: var(--surface) !important;
                border: 1px solid #444 !important;
                border-radius: 10px !important;
            }
            
            .stExpander .st-emotion-cache-1q7spjk {
                color: var(--text-primary) !important;
            }
            
            section[data-testid="stSidebar"] {
                background: linear-gradient(135deg, #1a2a3a, #0d1a26) !important;
                color: var(--text-primary) !important;
            }
            
            .st-emotion-cache-6qob1r {
                background: linear-gradient(135deg, #1a2a3a, #0d1a26) !important;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #2d2d2d;
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--primary);
                border-radius: 4px;
            }
            
            /* Progress bar */
            .stProgress > div > div > div {
                background: linear-gradient(90deg, var(--primary), #0096FF) !important;
            }
            
            /* Custom checkbox */
            .stCheckbox > label {
                color: var(--text-primary) !important;
            }
            
            /* Custom select box */
            .stSelectbox > div > div > div {
                background-color: var(--surface) !important;
                color: var(--text-primary) !important;
            }
        </style>
        """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0d1a26, #1a2a3a);
            padding: 36px 20px 28px 20px;
            border-radius: 16px;
            margin-bottom: 38px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            border: 1px solid #2d3a46;
        ">
            <div style="position:absolute;top:0;right:0;width:200px;height:200px;background: radial-gradient(circle, rgba(56,182,255,0.15) 0%, rgba(56,182,255,0) 70%);"></div>
            <h1 style="
                color: #fff !important;
                font-weight: 800;
                font-size: 2.8rem;
                margin-bottom: 12px;
                letter-spacing: 0.5px;
            ">
                AI-Powered Career Path Advisor
            </h1>
            <p style="
                color: #b0b0b0 !important;
                font-size: 1.2rem;
                margin-bottom: 0;
                line-height: 1.6;
                max-width: 800px;
            ">
                Discover your ideal technical career based on your unique skills, education, and experience.
                <br>
                <span style="color: var(--primary); font-weight: 600;">Upload your resume or enter details to get personalized recommendations!</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Initialize session state
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;margin-bottom:30px">
            <h2 style="color: var(--primary) !important;">Navigation</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: rgba(56, 182, 255, 0.1);
            padding: 16px;
            border-radius: 10px;
            border-left: 4px solid var(--primary);
            margin-bottom: 20px;
        ">
            <p style="margin-bottom: 8px; font-weight: 600; color: var(--primary);">🔍 Resume Analysis</p>
            <p style="margin-bottom: 8px; font-weight: 600; color: var(--primary);">💡 Career Recommendations</p>
            <p style="margin-bottom: 0; font-weight: 600; color: var(--primary);">📊 Market Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="
            background: rgba(76, 175, 80, 0.1);
            padding: 16px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 4px solid var(--secondary);
        ">
            <p style="font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">Need help?</p>
            <p style="color: var(--text-secondary); margin-bottom: 0;">Contact our career advisors:</p>
            <p style="color: var(--primary); font-weight: 600; margin-bottom: 0;">careersupport@example.com</p>
        </div>
        """, unsafe_allow_html=True)

    # Resume Upload Section
    with st.container():
        st.markdown("""
        <div style="
            background: #1e1e1e;
            padding: 16px 24px;
            border-radius: 12px;
            margin-bottom: 24px;
            border-left: 4px solid var(--primary);
        ">
            <h2 style="color: var(--primary); margin-bottom: 8px;">📋 Resume Analysis</h2>
            <p style="color: var(--text-secondary); margin-bottom: 0;">
                Upload your resume to automatically extract your skills, education, and experience.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)", 
            type=["pdf", "docx"],
            help="We'll analyze your skills, education, and experience automatically",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)
                    
                if not text.strip():
                    st.error("The uploaded file appears to be empty or couldn't be read properly.")
                else:
                    st.session_state.user_profile = {
                        "skills": extract_skills(text),
                        "education": extract_education(text),
                        "experience": extract_experience(text)
                    }
                    
                    st.success("✅ Resume parsed successfully! We've identified your key qualifications.")
                    
                    with st.expander("View extracted information", expanded=True):
                        st.subheader("🔍 Identified Skills")
                        if st.session_state.user_profile['skills']:
                            st.write(", ".join([f"`{skill}`" for skill in st.session_state.user_profile['skills']]))
                        else:
                            st.warning("No skills detected in the resume")
                            
                        st.subheader("🎓 Education Background")
                        for edu in st.session_state.user_profile['education']:
                            st.write(f"- {edu}")
                            
                        st.subheader("💼 Work Experience")
                        for exp in st.session_state.user_profile['experience']:
                            st.write(f"- {exp}")
            except Exception as e:
                st.error(f"⚠️ Error processing file: {str(e)}")

    # Career Recommendations Section
    if st.session_state.user_profile:
        with st.container():
            st.markdown("""
            <div style="
                background: #1e1e1e;
                padding: 16px 24px;
                border-radius: 12px;
                margin-bottom: 24px;
                border-left: 4px solid var(--primary);
            ">
                <h2 style="color: var(--primary); margin-bottom: 8px;">💡 Career Recommendations</h2>
                <p style="color: var(--text-secondary); margin-bottom: 0;">
                    Based on your profile, here are the most suitable career paths for you.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            recommendations = calculate_career_match(st.session_state.user_profile)
            
            if recommendations:
                display_career_recommendations(recommendations, TECH_CAREERS)
                
                # Top recommendation highlight
                top_career, top_score = recommendations[0]
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #1a2a3a, #0d1a26); padding: 36px 32px 28px 32px; border-radius: 16px; margin-top: 40px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid #2d3a46; position: relative; overflow: hidden;">
                        <div style="position:absolute;top:0;right:0;width:200px;height:200px;background: radial-gradient(circle, rgba(76,175,80,0.15) 0%, rgba(76,175,80,0) 70%;"></div>
                        <div style="display:flex;align-items:center;margin-bottom:20px;">
                            <div style="background: rgba(76, 175, 80, 0.2); padding: 8px 12px; border-radius: 6px; margin-right: 12px;">
                                <span style="font-size:24px;">🏆</span>
                            </div>
                            <h3 style="color:#fff; margin:0; font-size:1.5rem; font-weight:700;">Your Best Career Match</h3>
                        </div>
                        <h2 style="color:#4CAF50; margin-bottom:18px; font-size:2.2rem; font-weight:800; letter-spacing:0.5px;">{top_career}</h2>
                        <div style="display:flex;flex-wrap:wrap;gap:24px;margin-bottom:24px;">
                            <div style="flex:1;min-width:200px;">
                                <div style="background: rgba(56, 182, 255, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid var(--primary);">
                                    <p style="margin-bottom:6px;font-size:0.9rem;color:var(--text-secondary);">Match Score</p>
                                    <p style="margin:0;font-size:1.5rem;font-weight:700;color:var(--primary);">{top_score:.1f}%</p>
                                </div>
                            </div>
                            <div style="flex:1;min-width:200px;">
                                <div style="background: rgba(76, 175, 80, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid var(--secondary);">
                                    <p style="margin-bottom:6px;font-size:0.9rem;color:var(--text-secondary);">Salary Range</p>
                                    <p style="margin:0;font-size:1.5rem;font-weight:700;color:var(--secondary);">{TECH_CAREERS[top_career]['salary_range']}</p>
                                </div>
                            </div>
                            <div style="flex:1;min-width:200px;">
                                <div style="background: rgba(231, 76, 60, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid var(--error);">
                                    <p style="margin-bottom:6px;font-size:0.9rem;color:var(--text-secondary);">Market Demand</p>
                                    <p style="margin:0;font-size:1.5rem;font-weight:700;color:{'var(--success)' if TECH_CAREERS[top_career]['demand'] in ['High','Very High'] else 'var(--error)'};">{TECH_CAREERS[top_career]['demand']}</p>
                                </div>
                            </div>
                        </div>
                        <div style="margin-bottom:24px;">
                            <p style="font-weight:600;color:var(--text-primary);margin-bottom:8px;">Why this role suits you:</p>
                            <p style="margin:0;color:var(--text-secondary);line-height:1.6;">{TECH_CAREERS[top_career]['description']}</p>
                        </div>
                        <div style="display:flex;flex-wrap:wrap;gap:32px;margin-bottom:24px;">
                            <div style="flex:1;min-width:250px;">
                                <div style="background: rgba(56, 182, 255, 0.1); padding: 16px; border-radius: 8px;">
                                    <p style="font-weight:600;color:var(--primary);margin-bottom:12px;">🔧 Key Skills Needed</p>
                                    <div style="display:flex;flex-wrap:wrap;gap:8px;">
                                        {''.join([f"<span style='background: rgba(56, 182, 255, 0.2); color: var(--primary); padding: 4px 12px; border-radius: 16px; font-size: 0.85rem; display: inline-block; margin-bottom: 8px;'>{skill.title()}</span>" for skill in TECH_CAREERS[top_career]['required_skills']])}
                                    </div>
                                </div>
                            </div>
                            <div style="flex:1;min-width:250px;">
                                <div style="background: rgba(76, 175, 80, 0.1); padding: 16px; border-radius: 8px;">
                                    <p style="font-weight:600;color:var(--secondary);margin-bottom:12px;">🎓 Preferred Education</p>
                                    <div style="display:flex;flex-direction:column;gap:8px;">
                                        {''.join([f"<span style='background: rgba(76, 175, 80, 0.2); color: var(--secondary); padding: 4px 12px; border-radius: 16px; font-size: 0.85rem; display: inline-block; margin-bottom: 8px;'>{edu.title()}</span>" for edu in TECH_CAREERS[top_career]['preferred_education']])}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div style="text-align:center;">
                            <p style="color:var(--text-secondary);font-size:0.9rem;margin-bottom:0;">
                                Tip: Consider developing the highlighted skills to improve your match for this role!
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("No career recommendations could be generated based on the provided information.")

    # Manual Input Fallback
    with st.expander("Don't have a resume? Enter your details manually", expanded=False):
        with st.form("manual_input"):
            manual_skills = st.text_input(
                "Your skills (comma separated)", 
                help="e.g., Python, SQL, Data Analysis",
                placeholder="Enter your technical skills separated by commas"
            )
            manual_education = st.text_input(
                "Your highest degree", 
                help="e.g., B.Sc Computer Science",
                placeholder="Enter your highest education degree"
            )
            manual_experience = st.text_area(
                "Your work experience", 
                help="Briefly describe your work experience",
                placeholder="Describe your professional experience"
            )
            
            submitted = st.form_submit_button("Get Recommendations", type="primary")
            
            if submitted:
                if manual_skills or manual_education:
                    st.session_state.user_profile = {
                        "skills": [s.strip() for s in manual_skills.split(",") if s.strip()] if manual_skills else [],
                        "education": [manual_education] if manual_education else [],
                        "experience": [manual_experience] if manual_experience else []
                    }
                    st.rerun()
                else:
                    st.warning("Please provide at least your skills or education to get recommendations")

    # Footer
    st.markdown("""
        <div style="
            text-align:center;
            margin-top:48px;
            padding:28px 0;
            background: linear-gradient(135deg, #1a2a3a, #0d1a26);
            border-radius: 16px;
            border: 1px solid #2d3a46;
        ">
            <div style="margin-bottom:16px;">
                <span style="font-size:24px;">🚀</span>
            </div>
            <p style="
                color:var(--primary);
                font-size:1rem;
                font-weight:600;
                margin-bottom:8px;
            ">
                AI Career Path Advisor
            </p>
            <p style="
                color:var(--text-secondary);
                font-size:0.9rem;
                margin-bottom:0;
            ">
                &copy; 2024 Career Path Advisor. All rights reserved.
            </p>
            <p style="
                color:var(--text-secondary);
                font-size:0.8rem;
                margin-bottom:0;
                margin-top:8px;
            ">
                Made with <span style="color:#e25555;">❤️</span> for your future success
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()