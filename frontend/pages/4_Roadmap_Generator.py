import streamlit as st
import json
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules import roadmap_generator
from modules.roadmap_generator import generate_roadmap

def load_career_profiles(path='config/career_profiles.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    st.set_page_config(
        page_title="Roadmap Generator",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load career profiles
    try:
        career_profiles = load_career_profiles()
    except FileNotFoundError:
        st.error("Career profiles file not found. Please check your configuration.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading career profiles: {str(e)}")
        st.stop()

    if not career_profiles:
        st.warning("No career profiles found. Please check your configuration.")
        st.stop()

    with st.sidebar:
        st.title("🗺️ Roadmap Generator")
        st.subheader("Career Target")
        desired_career = st.selectbox(
            "Select your desired career path",
            sorted(career_profiles.keys()),
            help="Choose the career you want a roadmap for"
        )

        st.subheader("Your Skills")
        skills_text = st.text_area(
            "Enter your current skills (comma separated)",
            placeholder="Python, SQL, Project Management...",
            help="Separate each skill with a comma"
        )
        user_skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]

        generate_button = st.button(
            "Generate Roadmap",
            use_container_width=True,
            type="primary"
        )

    st.title("🗺️ Personalized Roadmap Generator")
    st.markdown("""
    Get a step-by-step learning and project roadmap to reach your dream career!
    """)

    if generate_button:
        if not user_skills:
            st.warning("Please enter your skills to generate a roadmap.")
            st.stop()
        if not desired_career:
            st.warning("Please select a desired career path.")
            st.stop()

        # --- Use static roadmap if available, else use AI-powered roadmap ---
        static_roles = roadmap_generator.generate_roadmap.__code__.co_consts[1].keys() if hasattr(roadmap_generator.generate_roadmap.__code__.co_consts[1], 'keys') else []
        # Fallback: try to get mapping from the function
        try:
            roadmap_sh_slugs = roadmap_generator.generate_roadmap.__code__.co_consts[1]
        except Exception:
            roadmap_sh_slugs = {}
        use_static = desired_career in roadmap_sh_slugs

        with st.spinner("Generating your personalized roadmap..."):
            roadmap = generate_roadmap(user_skills, desired_career, career_profiles)
            st.markdown(roadmap)
            st.download_button(
                label="📥 Download Roadmap (Markdown)",
                data=roadmap,
                file_name=f"{desired_career.replace(' ', '_')}_roadmap.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()