import streamlit as st
import json
import sys
import os

# Add project root (AI_CAREER_MENTOR) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    import modules.skill_gap_logic
except ImportError:
    st.error("Could not import skill_gap_logic module. Please check your project structure.")
    st.stop()

def app():
    # Set Streamlit theme using st.markdown (alternative to st.set_page_config)
    st.markdown(
        """
        <meta name="theme-color" content="#2E8B57">
        """,
        unsafe_allow_html=True
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .stButton>button {
        background-color: #2E8B57;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #3CB371;
        color: white;
    }
    .stProgress > div > div > div {
        background-color: #2E8B57;
    }
    .stMarkdown h1 {
        color: #2E8B57;
    }
    .stMarkdown h2 {
        color: #2E8B57;
    }
    .stMarkdown h3 {
        color: #2E8B57;
    }
    .css-1aumxhk {
        background-color: #F0F2F6;
        border-radius: 8px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar branding
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/learning.png", width=80)
        st.title("AI Career Mentor")
        st.markdown("---")
        st.markdown("### Navigation")
        st.markdown("- Skill Gap Analyzer")
        st.markdown("- Career Explorer")
        st.markdown("---")
        st.markdown("### About")
        st.markdown("This tool helps you identify the skills you need for your dream career.")

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

    # Main content
    st.title("🔍 Skill Gap Analyzer")
    st.markdown("""
    Identify the gap between your current skills and those required for your dream career.
    **Get personalized course recommendations to bridge the gap!**
    """)

    # Main area for user input
    st.header("📋 User Profile")

    # Career selection
    st.subheader("Career Target")
    desired_career = st.selectbox(
        "Select your desired career path",
        sorted(career_profiles.keys()),
        help="Choose the career you want to analyze skills for"
    )

    with st.expander("💡 See required skills for this career"):
        if desired_career in career_profiles:
            st.write(f"**Skills needed for {desired_career}:**")
            for skill in career_profiles[desired_career]:
                st.markdown(f"- {skill}")
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
                
                st.success("Analysis complete!")
                st.balloons()
                
                tab1, tab2, tab3 = st.tabs(["📊 Summary", "✅ Matched Skills", "📚 Learning Plan"])

                with tab1:
                    st.header("Skill Gap Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Required Skills", len(result["ideal_skills"]))
                    with col2:
                        st.metric("Skills You Have", len(result["matched_skills"]))
                    with col3:
                        st.metric("Skills to Learn", len(result["missing_skills"]))

                    progress = len(result["matched_skills"]) / len(result["ideal_skills"]) if result["ideal_skills"] else 0
                    st.progress(progress)
                    st.markdown(f"**You have {progress:.0%} of the required skills for {desired_career}**")

                    if result["missing_skills"]:
                        st.warning(f"**Focus on:** {', '.join(result['missing_skills'][:3])}...")
                    else:
                        st.success("🎉 Congratulations! You have all the required skills!")

                    with st.expander("🔎 Detailed comparison"):
                        st.write("**All required skills:**")
                        for skill in result["ideal_skills"]:
                            st.markdown(f"- {skill}")

                with tab2:
                    st.header("Your Matched Skills")
                    if result["matched_skills"]:
                        st.write(f"You already have these {len(result['matched_skills'])} skills needed for {desired_career}:")
                        for skill in result["matched_skills"]:
                            st.success(f"✓ {skill}")
                    else:
                        st.warning("No matching skills found. You'll need to learn everything from scratch.")

                with tab3:
                    st.header("Your Personalized Learning Plan")
                    if result["missing_skills"]:
                        st.write(f"Here are recommended resources to acquire the {len(result['missing_skills'])} missing skills:")
                        
                        for skill, url in result["course_suggestions"].items():
                            with st.container():
                                st.subheader(f"📚 {skill}")
                                st.markdown(f"[Udemy Course Link]({url})")
                                st.write("**Learning tips:**")
                                st.markdown("- Spend 1-2 hours daily practicing")
                                st.markdown("- Build a small project using this skill")
                                st.markdown("- Find a mentor or study group")
                                st.markdown("---")

                        st.download_button(
                            label="📥 Download Learning Plan",
                            data=json.dumps({
                                "career": desired_career,
                                "matched_skills": result["matched_skills"],
                                "missing_skills": result["missing_skills"],
                                "courses": result["course_suggestions"],
                            }, indent=2),
                            file_name=f"{desired_career.replace(' ', '_')}_learning_plan.json",
                            mime="application/json"
                        )
                    else:
                        st.success("No missing skills! You're ready for this career path.")

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

    # Career explorer
    st.markdown("---")
    with st.expander("🔍 Explore All Career Profiles"):
        selected_profile = st.selectbox(
            "Select a career to view details",
            sorted(career_profiles.keys()),
            key="career_explorer"
        )
        if selected_profile in career_profiles:
            st.write(f"### {selected_profile}")
            st.write("**Required Skills:**")
            cols = st.columns(3)
            skills = career_profiles[selected_profile]
            for i, skill in enumerate(skills):
                cols[i % 3].write(f"- {skill}")

if __name__ == "__main__":
    app()