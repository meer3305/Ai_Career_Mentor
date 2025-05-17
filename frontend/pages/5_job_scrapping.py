import streamlit as st
import pandas as pd
import json
from modules.job_scrapping import JobScraper # Assuming your class is in modules/job_scrapping.py

def load_career_profiles(file_path="config/career_profiles.json"):
    """Loads career profiles and skills from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure 'config/career_profiles.json' exists.")
        st.stop()
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON from '{file_path}'. Please check the file format for errors.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred loading career profiles: {e}")
        st.stop()
    return {}

def main():
    st.set_page_config(layout="centered", page_title="Job & Internship Finder", page_icon="✨")

    st.title("✨ Discover Career Opportunities ✨")
    st.markdown("Find jobs and internships based on career paths or custom searches.")

    st.sidebar.header("⚙️ Search Options")

    career_profiles = load_career_profiles()
    if not career_profiles:
        return

    search_mode = st.sidebar.radio(
        "🔍 **Choose Search Type:**",
        ("Career Path", "Custom Search"),
        help="Select 'Career Path' for predefined skill-based searches or 'Custom Search' to enter your own keywords."
    )

    query = ""
    selected_career = None
    if search_mode == "Career Path":
        career_choices = ["Select a Career Path"] + list(career_profiles.keys())
        selected_career = st.sidebar.selectbox(
            "🎯 **Select a Career Path:**",
            career_choices,
            index=0,
            help="Choose a predefined career path to search for relevant opportunities."
        )
        if selected_career != "Select a Career Path":
            skills = career_profiles.get(selected_career, [])
            query = ", ".join(skills)
            with st.sidebar.expander(f"💡 **Skills for {selected_career}:**"):
                st.write(", ".join(skills))
    else:
        query = st.sidebar.text_area(
            "🔑 **Enter Custom Keywords:**",
            placeholder="e.g., 'software engineer, Python, AI'",
            height=100,
            help="Enter specific keywords you're looking for. Separate multiple keywords with commas."
        )

    search_type = st.sidebar.radio(
        "💼 **Opportunity Type:**",
        ("Jobs", "Internships"),
        help="Select whether you are looking for full-time jobs or internships."
    )

    location = st.sidebar.text_input(
        "📍 **Location (optional):**",
        placeholder="e.g., 'Bangalore', 'Remote'",
        help="Enter a specific city or region. Leave blank for a broader search."
    )

    platform = None
    if search_type == "Jobs":
        platform = st.sidebar.selectbox(
            "🏢 **Select Job Platform:**",
            ("LinkedIn", "Remotive"),
            help="LinkedIn for general jobs, Remotive for remote-only positions."
        )
    elif search_type == "Internships":
        platform = st.sidebar.selectbox(
            "🏢 **Select Internship Platform:**",
            ("Internshala",),
            help="Internshala specializes in internships."
        )

    if st.sidebar.button("🚀 **Find Opportunities**"):
        if not query and search_mode == "Custom Search":
            st.error("⚠️ **Please enter keywords for a custom search.**")
            return
        if search_mode == "Career Path" and selected_career == "Select a Career Path":
            st.warning("⚠️ **Please select a career path to search.**")
            return
        if not platform:
            st.error("⚠️ **Please select a platform to search on.**")
            return

        search_term_display = selected_career if search_mode == "Career Path" else f"'{query}'"
        st.info(f"Searching for {search_type.lower()} opportunities for {search_term_display} {f'in {location}' if location else ''} on {platform}...")

        scraper = JobScraper(platform.lower())
        results = []
        with st.spinner(f"Fetching {search_type.lower()} results..."):
            if platform.lower() == "remotive":
                results = scraper.fetch_jobs(query)
            else:
                results = scraper.fetch_jobs(query, location)

        if results:
            output_title = f"🔍 Found {len(results)} results for "
            if search_mode == "Career Path" and selected_career:
                output_title += f"**{selected_career}** role"
            else:
                output_title += f"keywords **'{query}'**"
            if location:
                output_title += f" in **{location}**"
            output_title += f" on **{platform}**:"
            st.subheader(output_title)

            for index, job in enumerate(results):
                st.markdown("---")
                st.markdown(f"### ✨ **{job.get('title', 'N/A').strip()}**")
                st.markdown(f"**Company:** `{job.get('company', 'N/A').strip()}`")

                display_location = job.get('location', 'N/A').strip()
                if not display_location or display_location.lower() == 'n/a':
                    display_location = location if location else 'N/A'
                st.markdown(f"**Location:** `{display_location}`")

                if 'salary' in job and job['salary'] and job['salary'] != 'N/A':
                    st.markdown(f"💰 **Salary/Stipend:** `{job['salary'].strip()}`")
                elif 'stipend' in job and job['stipend'] and job['stipend'] != 'N/A':
                    st.markdown(f"💰 **Stipend:** `{job['stipend'].strip()}`")
                else:
                    st.markdown("💰 **Salary/Stipend:** *Not specified*")

                if 'type' in job and job['type']:
                    st.markdown(f"**Job Type:** `{job.get('type').strip()}`")
                if 'tags' in job and job['tags']:
                    tags_str = ", ".join(tag.strip() for tag in job['tags'] if tag.strip())
                    if tags_str:
                        st.markdown(f"**Tags:** `{tags_str}`")

                link = job.get('link', 'N/A')
                if link and link != 'N/A':
                    st.markdown(f"[🔗 **View Opportunity**]({link})")
                else:
                    st.markdown("💔 **Link:** *Not Available*")
            st.markdown("---")

        else:
            output_message = "😔 No matching opportunities found"
            if search_mode == "Career Path" and selected_career:
                output_message += f" for the **{selected_career}** role"
            elif query:
                output_message += f" for the keywords **'{query}'**"
            if location:
                output_message += f" in **{location}**"
            output_message += f" on **{platform}**."
            st.info(output_message + " Try refining your search criteria.")

if __name__ == "__main__":
    main()