import streamlit as st
import os
import pandas as pd
import json
from utils.parser import ResumeParser
from utils.groq_analyzer import GroqAnalyzer

# Set page configuration
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

if 'job_description' not in st.session_state:
    st.session_state.job_description = ""

if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
    
# API key now handled through environment variables
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = None
    
if 'groq_analysis' not in st.session_state:
    st.session_state.groq_analysis = None

# Helper functions
def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary location and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def process_resume(file):
    """Process the uploaded resume file"""
    try:
        # Get file extension
        file_extension = file.name.split('.')[-1].lower()
        
        # Initialize parser
        parser = ResumeParser()
        
        # Parse resume
        resume_text = parser.parse(file, file_extension)
        
        if isinstance(resume_text, str) and resume_text.startswith("Error"):
            st.error(resume_text)
            return None
        
        # Extract contact info and sections
        contact_info = parser.extract_contact_info()
        sections = parser.extract_sections()
        
        # Initialize results without Groq analysis first
        results = {
            'resume_text': resume_text,
            'contact_info': contact_info,
            'sections': sections,
            'readability': {}  # Will be filled later
        }
        
        # Initialize Groq analyzer (will use default API key from .env file)
        groq_analyzer = GroqAnalyzer()
        
        # Analyze resume with Groq
        groq_result = groq_analyzer.analyze_resume(
            resume_text=resume_text,
            job_description=st.session_state.job_description if st.session_state.job_description else None
        )
        
        # Store Groq analysis result
        st.session_state.groq_analysis = groq_result
        
        # Generate suggestions based on Groq analysis result
        if groq_result.get('error'):
            results['suggestions'] = [f"Error with Groq analysis: {groq_result['error']}"]
        else:
            # Try to parse Groq analysis JSON
            try:
                analysis_data = json.loads(groq_result['analysis'])
                suggestions = analysis_data.get('specific_suggestions', [])
                if not suggestions:
                    suggestions = analysis_data.get('improvement_areas', [])
                results['suggestions'] = suggestions
            except Exception as e:
                results['suggestions'] = [f"Error parsing Groq analysis: {str(e)}"]
        
        return results
    
    except Exception as e:
        st.error(f"Error processing resume: {e}")
        return None

# Main application UI
st.markdown('<h1 class="main-header">Resume Analyzer</h1>', unsafe_allow_html=True)
st.markdown('Upload your resume to get insights and improvement suggestions.')

# Sidebar with file upload and options
with st.sidebar:
    st.markdown('<h2 class="sub-header">Upload Resume</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a resume file", 
        type=["pdf", "docx", "txt"],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )
    
    st.markdown('<p class="hint-text">Supported formats: PDF, DOCX, TXT</p>', unsafe_allow_html=True)
    
    st.markdown('---')
    
    st.markdown('<h2 class="sub-header">Compare with Job Description</h2>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste Job Description (Optional)",
        placeholder="Paste the job description here to compare with your resume...",
        height=150
    )
    
    if job_description != st.session_state.job_description:
        st.session_state.job_description = job_description
    
    # Removed Groq API Key input section
    
    analyze_button = st.button("Analyze Resume", type="primary", disabled=not uploaded_file)

# Process the resume when the analyze button is clicked
if analyze_button and uploaded_file:
    with st.spinner("Analyzing your resume... This may take a moment."):
        results = process_resume(uploaded_file)
        
        if results:
            st.session_state.resume_data = results
            st.session_state.analysis_done = True
            st.success("Analysis completed successfully!")
            
            # Auto-scroll to results
            st.rerun()

# Display results if analysis is done
if st.session_state.analysis_done and st.session_state.resume_data:
    results = st.session_state.resume_data
    
    # Create tabs for different sections of the analysis
    tabs = st.tabs(["Overview", "AI Analysis", "Job Comparison", "Suggestions", "Raw Text"])
    
    # Overview Tab
    with tabs[0]:
        st.markdown('<h2 class="sub-header">Resume Overview</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.markdown("### Contact Information")
            
            contact_info = results['contact_info']
            st.markdown(f"📧 **Email:** {contact_info.get('email', 'NULL')}")
            st.markdown(f"📱 **Phone:** {contact_info.get('phone', 'NULL')}")
            st.markdown(f"💼 **LinkedIn:** {contact_info.get('linkedin', 'NULL')}")
            st.markdown(f"🔥 **GitHub:** {contact_info.get('github', 'NULL')}")
            st.markdown(f"🌐 **Website:** {contact_info.get('website', 'NULL')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.markdown("### Document Stats")
            
            # Calculate basic stats
            word_count = len(results['resume_text'].split())
            sentences = int(len(results['resume_text'].split('.')))
            
            st.markdown(f"📝 **Word Count:** {word_count}")
            st.markdown(f"📋 **Sentences:** {sentences}")
            st.markdown(f"📚 **Sections Found:** {len(results['sections'])}")
            st.markdown(f"🔧 **AI Analysis:** Enabled")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sections Found
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("### Resume Sections")
        
        sections = results['sections']
        if sections:
            # Define a specific order for the sections
            section_order = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications']
            
            # Display sections in the defined order
            for section_name in section_order:
                if section_name in sections and sections[section_name].strip():
                    with st.expander(f"{section_name.title()}"):
                        st.markdown(f"```\n{sections[section_name]}\n```")
            
            # Display any additional sections not in our predefined order
            other_sections = [s for s in sections if s not in section_order and sections[s].strip()]
            for section_name in other_sections:
                with st.expander(f"{section_name.title()}"):
                    st.markdown(f"```\n{sections[section_name]}\n```")
        else:
            st.info("No clear sections were identified in your resume. Consider using clear section headers.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Analysis Tab
    with tabs[1]:
        st.markdown('<h2 class="sub-header">AI-Powered Resume Analysis</h2>', unsafe_allow_html=True)
        
        if st.session_state.groq_analysis and st.session_state.groq_analysis.get('error'):
            st.error(f"Error with Groq analysis: {st.session_state.groq_analysis['error']}")
        elif st.session_state.groq_analysis and st.session_state.groq_analysis.get('analysis'):
            try:
                # Parse the JSON response from Groq
                analysis_data = json.loads(st.session_state.groq_analysis['analysis'])
                
                # Overall Assessment
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown("### Overall Assessment")
                st.write(analysis_data.get('overall_assessment', "No overall assessment available."))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Key Strengths & Improvement Areas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown("### Key Strengths")
                    strengths = analysis_data.get('key_strengths', [])
                    if strengths:
                        for strength in strengths:
                            st.markdown(f"✅ {strength}")
                    else:
                        st.info("No key strengths identified.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown("### Improvement Areas")
                    improvements = analysis_data.get('improvement_areas', [])
                    if improvements:
                        for area in improvements:
                            st.markdown(f"🔍 {area}")
                    else:
                        st.success("No specific improvement areas identified.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Structure & Language Feedback
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown("### Resume Structure & Language")
                
                expander1 = st.expander("Structure Assessment")
                with expander1:
                    st.write(analysis_data.get('structure_feedback', "No structure feedback available."))
                    
                expander2 = st.expander("Language & Phrasing")
                with expander2:
                    st.write(analysis_data.get('language_feedback', "No language feedback available."))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Red Flags
                red_flags = analysis_data.get('red_flags', [])
                if red_flags:
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown("### Potential Red Flags")
                    for flag in red_flags:
                        st.markdown(f"⚠️ {flag}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error parsing AI analysis: {str(e)}")
                st.code(st.session_state.groq_analysis['analysis'], language="json")
        else:
            st.info("Click 'Analyze Resume' to generate AI-powered analysis of your resume.")
            with st.expander("What does the AI analyze?"):
                st.markdown("""
                The AI analysis evaluates multiple aspects of your resume including:
                - Overall impact and effectiveness
                - Structure and organization
                - Language and phrasing
                - Achievement descriptions
                - Potential red flags
                - Match with job descriptions (if provided)
                
                The analysis is powered by Groq's large language models, which have been trained on millions of professional documents.
                """)

    
    # Job Comparison Tab
    with tabs[2]:
        st.markdown('<h2 class="sub-header">Job Description Comparison</h2>', unsafe_allow_html=True)
        
        if not st.session_state.job_description:
            st.info("Paste a job description in the sidebar to compare it with your resume.")
        elif st.session_state.groq_analysis and st.session_state.groq_analysis.get('analysis'):
            try:
                # Parse the JSON response from Groq
                analysis_data = json.loads(st.session_state.groq_analysis['analysis'])
                
                # Check if job match data is available
                if 'job_match' in analysis_data:
                    job_match = analysis_data['job_match']
                    
                    # Overall Assessment
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown("### Job Match Assessment")
                    st.write(job_match.get('match_assessment', "No job match assessment available."))
                    
                    # Display alignment score if available
                    if 'alignment_score' in job_match:
                        score = job_match['alignment_score']
                        st.progress(score/100)
                        
                        if score > 75:
                            st.success(f"Great match! Your resume aligns {score}% with the job description.")
                        elif score > 50:
                            st.info(f"Good match. Your resume shows {score}% alignment with the job description.")
                        else:
                            st.warning(f"Your resume could be better aligned with this job description. Current match: {score}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Missing Keywords
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown("### Missing Keywords")
                    
                    missing_keywords = job_match.get('missing_keywords', [])
                    if missing_keywords:
                        st.write("Consider adding these keywords from the job description to your resume:")
                        keyword_chunks = [missing_keywords[i:i+5] for i in range(0, len(missing_keywords), 5)]
                        for chunk in keyword_chunks[:6]:  # Limit to first 30 keywords
                            st.markdown(', '.join([f"`{word}`" for word in chunk]))
                        
                        if len(keyword_chunks) > 6:
                            st.info(f"Plus {len(missing_keywords) - 30} more keywords not shown.")
                    else:
                        st.success("No significant keywords are missing!")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Recommendations
                    if 'recommendations' in job_match and job_match['recommendations']:
                        st.markdown('<div class="result-section">', unsafe_allow_html=True)
                        st.markdown("### Tailoring Recommendations")
                        
                        for i, rec in enumerate(job_match['recommendations'], 1):
                            st.markdown(f"**{i}.** {rec}")
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No job comparison data available. This may happen if the AI analysis focused on other aspects of your resume.")
                    st.info("Try analyzing your resume again with the job description provided in the sidebar.")
                    
            except Exception as e:
                st.error(f"Error parsing job comparison data: {str(e)}")
        else:
            st.info("Click 'Analyze Resume' to generate a comparison between your resume and the job description.")
    
    # Suggestions Tab
    with tabs[3]:
        st.markdown('<h2 class="sub-header">Improvement Suggestions</h2>', unsafe_allow_html=True)
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        
        suggestions = results['suggestions']
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"**{i}.** {suggestion}")
        else:
            st.success("No specific suggestions found. Your resume looks good!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # General Tips
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("### General Resume Tips")
        
        general_tips = [
            "Use bullet points to highlight accomplishments and make your resume scannable.",
            "Tailor your resume for each job application by matching keywords from the job description.",
            "Quantify your achievements with numbers and percentages when possible.",
            "Keep your resume concise - typically 1-2 pages depending on experience level.",
            "Use action verbs to start bullet points (e.g., 'Managed', 'Developed', 'Led').",
            "Proofread carefully to eliminate spelling and grammar errors.",
            "Include a strong summary or objective statement at the top of your resume."
        ]
        
        for tip in general_tips:
            st.markdown(f"💡 {tip}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Raw Text Tab
    with tabs[4]:
        st.markdown('<h2 class="sub-header">Raw Resume Text</h2>', unsafe_allow_html=True)
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        
        st.text_area(
            "Extracted Text",
            value=results['resume_text'],
            height=400
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Instructions if no file is uploaded yet
if not st.session_state.analysis_done:
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("### How to Use This Tool")
    
    st.markdown("""
    1. **Upload your resume** using the file uploader in the sidebar (PDF, DOCX, or TXT formats).
    2. **Optionally, paste a job description** to compare your resume against it.
    3. **Click 'Analyze Resume'** to process your document.
    4. **Review the detailed analysis** across different tabs:
        - Overview of your resume content and structure
        - Skills analysis and visualization
        - Content analysis with word frequency and readability metrics
        - Job description comparison (if provided)
        - Specific improvement suggestions
    """)
    
    st.markdown("### Why Use Resume Analyzer?")
    st.markdown("""
    - **Identify Missing Keywords** that could help your resume pass ATS (Applicant Tracking Systems)
    - **Improve Readability** to make your resume more effective
    - **Get Actionable Suggestions** to enhance your resume content
    - **Visualize Your Skills** to better understand your strengths
    - **Tailor Your Resume** to specific job descriptions
    """)
    st.markdown('</div>', unsafe_allow_html=True)
