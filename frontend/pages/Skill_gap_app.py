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
    # Set page config
    # Set Streamlit page config (alternative to st.set_page_config)
    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Skill Gap Analyzer</title>
        <link rel="icon" href="https://img.icons8.com/color/96/000000/learning.png">
        """,
        unsafe_allow_html=True
    )

    # Sidebar branding
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/learning.png", width=80)
        st.markdown("<h2 style='color:#4F8BF9;'>AI Career Mentor</h2>", unsafe_allow_html=True)
        st.markdown("---")

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

    # Main area for user input
    st.markdown("## 📋 User Profile")

    # Career selection
    st.subheader("Career Target")
    desired_career = st.selectbox(
        "Select your desired career path",
        sorted(career_profiles.keys()),
        help="Choose the career you want to analyze skills for"
    )

    with st.expander("💡 See required skills for this career"):
        if desired_career in career_profiles:
            st.write(f"Skills needed for **{desired_career}**:")
            st.markdown(
                "<ul>" + "".join([f"<li>{skill}</li>" for skill in career_profiles[desired_career]]) + "</ul>",
                unsafe_allow_html=True
            )
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

    # Main content
    st.markdown(
        "<h1 style='color:#4F8BF9;'>🔍 Skill Gap Analyzer</h1>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div style='font-size:18px; color:#fff;'>
    Identify the gap between your current skills and those required for your dream career.<br>
    <b>Get personalized course recommendations to bridge the gap!</b>
    </div>
    """, unsafe_allow_html=True)

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
                # Enhanced Results UI with improved text visibility (black text on light backgrounds)
                tab1, tab2, tab3 = st.tabs([
                    "📊 <span style='color:black;'>Summary</span>", 
                    "✅ <span style='color:black;'>Matched Skills</span>", 
                    "📚 <span style='color:black;'>Learning Plan</span>"
                ])

                with tab1:
                    st.markdown("<h3 style='color:black;'>Skill Gap Summary</h3>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Required Skills", len(result["ideal_skills"]))
                    with col2:
                        st.metric("Skills You Have", len(result["matched_skills"]))
                    with col3:
                        st.metric("Skills to Learn", len(result["missing_skills"]))

                    progress = len(result["matched_skills"]) / len(result["ideal_skills"]) if result["ideal_skills"] else 0
                    st.progress(progress)
                    st.markdown(
                        f"<span style='color:black;font-size:16px;'>You have <b>{progress:.0%}</b> of the required skills for <b>{desired_career}</b></span>",
                        unsafe_allow_html=True
                    )

                    if result["missing_skills"]:
                        st.markdown(
                            f"<div style='color:#d84315; background:#fff3e0; padding:10px; border-radius:6px;'><b>🔍 Focus on:</b> {', '.join(result['missing_skills'][:3])}...</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div style='color:#388e3c; background:#e8f5e9; padding:10px; border-radius:6px;'><b>🎉 Congratulations! You have all the required skills!</b></div>",
                            unsafe_allow_html=True
                        )

                    with st.expander("🔎 Detailed comparison"):
                        st.markdown("<span style='color:black;'><b>All required skills:</b></span>", unsafe_allow_html=True)
                        st.markdown(
                            "<ul style='color:black;'>" + "".join([f"<li>{skill}</li>" for skill in result["ideal_skills"]]) + "</ul>",
                            unsafe_allow_html=True
                        )

                with tab2:
                    st.markdown("<h3 style='color:black;'>Your Matched Skills</h3>", unsafe_allow_html=True)
                    if result["matched_skills"]:
                        st.markdown(
                            f"<span style='color:black;'>You already have these <b>{len(result['matched_skills'])}</b> skills needed for <b>{desired_career}</b>:</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<ul style='color:#388e3c;font-weight:bold;'>" +
                            "".join([f"<li style='color:#388e3c;font-weight:bold;font-size:16px;'>{skill}</li>" for skill in result["matched_skills"]]) +
                            "</ul>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div style='color:#d84315; background:#fff3e0; padding:10px; border-radius:6px;'>No matching skills found. You'll need to learn everything from scratch.</div>",
                            unsafe_allow_html=True
                        )

                with tab3:
                    st.markdown("<h3 style='color:black;'>Your Personalized Learning Plan</h3>", unsafe_allow_html=True)
                    if result["missing_skills"]:
                        st.markdown(
                            f"<span style='color:black;'>Here are recommended resources to acquire the <b>{len(result['missing_skills'])}</b> missing skills:</span>",
                            unsafe_allow_html=True
                        )
                        for skill, url in result["course_suggestions"].items():
                            st.markdown(f"""
                            <div style="padding: 15px; margin-bottom: 15px; background-color: #f5f5f5; border-left: 4px solid #1976d2; color:black;">
                                <h4 style="color:#1976d2;">📚 {skill}</h4>
                                <p><a href="{url}" target="_blank" style="color:#1976d2;">Udemy Course Link</a></p>
                                <p style="color:black;"><strong>Learning tips:</strong></p>
                                <ul style="color:black;">
                                    <li>Spend 1-2 hours daily practicing</li>
                                    <li>Build a small project using this skill</li>
                                    <li>Find a mentor or study group</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)

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
                        st.markdown(
                            "<div style='color:#388e3c; background:#e8f5e9; padding:10px; border-radius:6px;'><b>No missing skills! You're ready for this career path.</b></div>",
                            unsafe_allow_html=True
                        )
                        st.balloons()

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

    # Career explorer
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
            for i, skill in enumerate(skills):
                cols[i % 3].write(f"- {skill}")

# Ensure the app runs if this file is executed directly
if __name__ == "__main__":
    app()
