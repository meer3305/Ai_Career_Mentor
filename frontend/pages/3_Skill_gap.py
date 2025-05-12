import streamlit as st
import json
import modules
import modules.skill_gap_logic

def main():
    # Set page config
    st.set_page_config(
        page_title="Skill Gap Analyzer", 
        page_icon="📊", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # # Custom CSS for better styling
    # st.markdown("""
    # <style>
    #     .stProgress > div > div > div > div {
    #         background-color: #4CAF50;
    #     }
    #     .st-bb {
    #         background-color: #f0f2f6;
    #     }
    #     .st-at {
    #         background-color: #ffffff;
    #     }
    #     .skill-card {
    #         padding: 15px;
    #         border-radius: 10px;
    #         box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    #         margin-bottom: 15px;
    #     }
    #     .matched-skill {
    #         border-left: 5px solid #4CAF50;
    #     }
    #     .missing-skill {
    #         border-left: 5px solid #FF9800;
    #     }
    # </style>
    # """, unsafe_allow_html=True)
    
    # Load career profiles
    try:
        career_profiles = modules.skill_gap_logic.load_career_profiles()
    except FileNotFoundError:
        st.error("Career profiles file not found. Please check your configuration.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading career profiles: {str(e)}")
        st.stop()
    
    if not career_profiles:
        st.warning("No career profiles found. Please check your configuration.")
        st.stop()
    
    # Sidebar for user input
    with st.sidebar:
        st.title("📋 User Profile")
        
        # Career selection first so we can show relevant examples
        st.subheader("Career Target")
        desired_career = st.selectbox(
            "Select your desired career path", 
            sorted(career_profiles.keys()),
            help="Choose the career you want to analyze skills for"
        )
        
        # Show example skills for selected career
        with st.expander("💡 See required skills for this career"):
            if desired_career in career_profiles:
                st.write(f"Skills needed for {desired_career}:")
                st.write(career_profiles[desired_career])
            else:
                st.write("No skill data available for this career.")
        
        st.subheader("Your Skills")
        input_method = st.radio(
            "How would you like to input your skills?", 
            ("Type them", "Upload a file"),
            horizontal=True
        )
        
        user_skills = []
        if input_method == "Type them":
            skills_text = st.text_area(
                "Enter your skills (comma separated)", 
                placeholder="Python, SQL, Project Management...",
                help="Separate each skill with a comma"
            )
            if skills_text:
                user_skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
        else:
            uploaded_file = st.file_uploader(
                "Upload your skills file", 
                type=["txt", "json", "csv"],
                help="Upload a text file with comma-separated skills or a JSON file with skills array"
            )
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.json'):
                        skills_data = json.load(uploaded_file)
                        if isinstance(skills_data, list):
                            user_skills = [str(skill).strip() for skill in skills_data]
                        elif isinstance(skills_data, dict):
                            user_skills = [str(skill).strip() for skill in skills_data.get('skills', [])]
                    else:
                        skills_text = uploaded_file.read().decode("utf-8")
                        user_skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        analyze_button = st.button(
            "Analyze Skill Gap", 
            use_container_width=True,
            type="primary"
        )
    
    # Main content area
    st.title("🔍 Skill Gap Analyzer")
    st.markdown("""
    Identify the gap between your current skills and those required for your dream career.
    Get personalized course recommendations to bridge the gap!
    """)
    
    if analyze_button:
        if not user_skills:
            st.warning("Please enter or upload your skills to analyze")
            st.stop()
        
        if not desired_career:
            st.warning("Please select a desired career path")
            st.stop()
        
        with st.spinner("Analyzing your skill gap..."):
            try:
                result = modules.skill_gap_logic.analyze_skill_gap(user_skills, desired_career, career_profiles)
                
                # Results in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Summary", "✅ Matched Skills", "📚 Learning Plan"])
                
                with tab1:
                    st.subheader("Skill Gap Summary")
                    
                    # Metrics columns
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Required Skills", len(result["ideal_skills"]))
                    with col2:
                        st.metric("Skills You Have", len(result["matched_skills"]))
                    with col3:
                        st.metric("Skills to Learn", len(result["missing_skills"]))
                    
                    # Progress visualization
                    progress = len(result["matched_skills"]) / len(result["ideal_skills"]) if result["ideal_skills"] else 0
                    st.progress(progress)
                    st.caption(f"You have {progress:.0%} of the required skills for {desired_career}")
                    
                    # Visual skill distribution
                    if result["missing_skills"]:
                        st.warning(f"🔍 Focus on: {', '.join(result['missing_skills'][:3])}...")
                    else:
                        st.success("🎉 Congratulations! You have all the required skills!")
                    
                    # Quick comparison
                    with st.expander("🔎 Detailed comparison"):
                        st.write("**All required skills:**")
                        st.write(result["ideal_skills"])
                
                with tab2:
                    st.subheader("Your Matched Skills")
                    if result["matched_skills"]:
                        st.write(f"You already have these {len(result['matched_skills'])} skills needed for {desired_career}:")
                        for skill in result["matched_skills"]:
                            st.markdown(f"""
                            <div class="skill-card matched-skill">
                                ✓ {skill}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No matching skills found. You'll need to learn everything from scratch.")
                
                with tab3:
                    st.subheader("Your Personalized Learning Plan")
                    if result["missing_skills"]:
                        st.write(f"Here are recommended resources to acquire the {len(result['missing_skills'])} missing skills:")
                        
                        for skill, url in result["course_suggestions"].items():
                            st.markdown(f"""
                            <div class="skill-card missing-skill">
                                <h4>📚 {skill}</h4>
                                <p><a href="{url}" target="_blank">Udemy Course Link</a></p>
                                <p><strong>Learning tips:</strong></p>
                                <ul>
                                    <li>Spend 1-2 hours daily practicing</li>
                                    <li>Build a small project using this skill</li>
                                    <li>Find a mentor or study group</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Learning Plan",
                            data=json.dumps({
                                "career": desired_career,
                                "matched_skills": result["matched_skills"],
                                "missing_skills": result["missing_skills"],
                                "courses": result["course_suggestions"],
                                "analysis_date": str(st.session_state.get("analysis_time", ""))
                            }, indent=2),
                            file_name=f"{desired_career.replace(' ', '_')}_learning_plan.json",
                            mime="application/json"
                        )
                    else:
                        st.success("No missing skills! You're ready for this career path.")
                        st.balloons()
                
                # Store analysis time
                st.session_state.analysis_time = st.session_state.get("analysis_time", "")
            
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
    
    # Career explorer section
    st.markdown("---")
    with st.expander("🔍 Explore All Career Profiles"):
        selected_profile = st.selectbox(
            "Select a career to view details", 
            sorted(career_profiles.keys())
        )
        if selected_profile in career_profiles:
            st.write(f"### {selected_profile}")
            st.write("**Required Skills:**")
            cols = st.columns(3)
            skills = career_profiles[selected_profile]
            
            # Display skills in 3 columns
            for i, skill in enumerate(skills):
                cols[i % 3].write(f"- {skill}")

if __name__ == "__main__":
    main()