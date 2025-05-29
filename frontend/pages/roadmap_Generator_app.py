def app():    
    import streamlit as st
    import json
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

    from modules import roadmap_generator
    from modules.roadmap_generator import generate_roadmap

    def load_career_profiles(path='config/career_profiles.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Streamlit Page Title and Icon (alternative to set_page_config)
    st.markdown(
        "<h1 style='text-align: left;'>🗺️ Roadmap Generator</h1>",
        unsafe_allow_html=True
    )

    # Load Profiles
    try:
        career_profiles = load_career_profiles()
    except Exception as e:
        st.error(f"Failed to load career profiles: {e}")
        return

    if not career_profiles:
        st.warning("No career profiles found.")
        return

    # Main Page
    st.title("📍 Personalized Roadmap Generator")
    st.markdown("Get a **step-by-step learning & project roadmap** to reach your dream career based on your current skills.")

    st.subheader("🗺️ Roadmap Generator")
    desired_career = st.selectbox(
        "🎯 Desired Career Path",
        sorted(career_profiles.keys()),
        help="Choose the career you want a roadmap for"
    )

    skills_input = st.text_area(
        "🛠️ Your Current Skills (comma-separated)",
        placeholder="Python, SQL, Project Management..."
    )
    user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    generate_button = st.button("🚀 Generate Roadmap", type="primary")

    if generate_button:
        if not user_skills:
            st.warning("⚠️ Please enter your skills to generate a roadmap.")
            return
        if not desired_career:
            st.warning("⚠️ Please select a career path.")
            return

        with st.spinner("🔍 Generating roadmap... please wait"):
            try:
                roadmap_md = generate_roadmap(
                    user_skills=user_skills,
                    desired_career=desired_career,
                    profiles=career_profiles,
                    api_key="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"
                )
                st.markdown(roadmap_md, unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Roadmap (Markdown)",
                    data=roadmap_md,
                    file_name=f"{desired_career.replace(' ', '_')}_roadmap.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ Roadmap generation failed: {e}")
