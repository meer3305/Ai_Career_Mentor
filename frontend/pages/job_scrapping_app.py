def app():
    import streamlit as st
    import pandas as pd
    import json
    import sys
    import os

    # Add project root (AI_CAREER_MENTOR) to sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

    from modules.job_scrapping import JobScraper

    # Apply custom theme and cool gradient background
    st.markdown("""
    <style>
    :root {
        --primary: #FF1744;
        --secondary: #FF4081;
        --bg: #181A20;
        --text: #F3F6F9;
        --card: #23272F;
        --accent: #FFD600;
        --shadow: 0 4px 24px 0 rgba(255,23,68,0.08);
    }
    .stApp {
        background: linear-gradient(135deg, #23272F 0%, #181A20 100%);
        min-height: 100vh;
    }
    .stButton > button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow) !important;
        font-weight: bold !important;
        outline: 2px solid #fff !important;
    }
    .stButton > button:hover, .stButton > button:focus {
        background-color: #D50000 !important;
        transform: scale(1.05) !important;
        color: #FFD600 !important;
        outline: 2px solid #FFD600 !important;
    }
    .stTextInput > div > input,
    .stTextArea > div > textarea {
        background-color: var(--card);
        color: var(--text);
        border: 2px solid var(--primary);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    .stTextInput > div > input:focus,
    .stTextArea > div > textarea:focus {
        outline: none;
        border-color: var(--accent);
    }
    .stRadio [data-baseweb="radio"] {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .stRadio [data-baseweb="radio"] input[type="radio"] {
        appearance: none;
        -webkit-appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid var(--primary);
        background-color: #fff;
        outline: none;
        cursor: pointer;
        position: relative;
        margin-right: 10px;
    }
    .stRadio [data-baseweb="radio"] input[type="radio"]:checked::before {
        content: '';
        position: absolute;
        top: 4px;
        left: 4px;
        width: 10px;
        height: 10px;
        background-color: var(--primary);
        border-radius: 50%;
    }
    .stRadio [data-baseweb="radio"] label {
        color: var(--text) !important;
        font-size: 1rem;
        cursor: pointer;
    }
    .skill-card {
        background-color: var(--card);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }
    /* Skill chip styling */
    .skill-chip {
        display: inline-block;
        background: var(--secondary);
        color: #fff;
        border-radius: 16px;
        padding: 0.3em 1em;
        margin: 0.2em 0.3em 0.2em 0;
        font-size: 0.95em;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(255,64,129,0.08);
        letter-spacing: 0.02em;
    }
    </style>
    """, unsafe_allow_html=True)

    def load_career_profiles(file_path="config/career_profiles.json"):
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
        st.title("✨ Discover Career Opportunities ✨")
        st.markdown("Find jobs and internships based on career paths or custom searches.", unsafe_allow_html=True)

        career_profiles = load_career_profiles()
        if not career_profiles:
            return

        st.header("⚙️ Search Options")

        search_mode = st.radio(
            "🔍 **Choose Search Type:**",
            ("Career Path", "Custom Search"),
            help="Select 'Career Path' for predefined skill-based searches or 'Custom Search' to enter your own keywords."
        )

        query = ""
        selected_career = None
        if search_mode == "Career Path":
            career_choices = ["Select a Career Path"] + list(career_profiles.keys())
            selected_career = st.selectbox(
                "🎯 **Select a Career Path:**",
                career_choices,
                index=0,
                help="Choose a predefined career path to search for relevant opportunities."
            )
            if selected_career != "Select a Career Path":
                skills = career_profiles.get(selected_career, [])
                # Styled skill chips
                skills_html = " ".join([f"<span class='skill-chip'>{skill}</span>" for skill in skills])
                st.markdown(
                    f"<div style='margin-bottom:0.5em;'><strong>Skills for {selected_career}:</strong> {skills_html}</div>",
                    unsafe_allow_html=True
                )
                query = ", ".join(skills)
        else:
            query = st.text_area(
                "🔑 **Enter Custom Keywords:**",
                placeholder="e.g., 'software engineer, Python, AI'",
                height=100,
                help="Enter specific keywords you're looking for. Separate multiple keywords with commas."
            )

        search_type = st.radio(
            "💼 **Opportunity Type:**",
            ("Jobs", "Internships"),
            help="Select whether you are looking for full-time jobs or internships."
        )

        location = st.text_input(
            "📍 **Location (optional):**",
            placeholder="e.g., 'Bangalore', 'Remote'",
            help="Enter a specific city or region. Leave blank for a broader search."
        )

        platform = None
        if search_type == "Jobs":
            platform = st.selectbox(
                "🏢 **Select Job Platform:**",
                ("LinkedIn", "Remotive"),
                help="LinkedIn for general jobs, Remotive for remote-only positions."
            )
        elif search_type == "Internships":
            platform = st.selectbox(
                "🏢 **Select Internship Platform:**",
                ("Internshala",),
                help="Internshala specializes in internships."
            )

        if st.button("🚀 **Find Opportunities**"):
            if not query and search_mode == "Custom Search":
                st.error("⚠️ **Please enter keywords for a custom search.**")
                return
            if search_mode == "Career Path" and selected_career == "Select a Career Path":
                st.warning("⚠️ **Please select a career path to search.**")
                return
            if not platform:
                st.error("⚠️ **Please select a platform to search on.**")
                return

            with st.spinner(f"🔍 Searching for {search_type.lower()} opportunities..."):
                try:
                    scraper = JobScraper(platform.lower())
                    results = []
                    
                    if platform.lower() == "remotive":
                        results = scraper.fetch_jobs(query)
                    else:
                        results = scraper.fetch_jobs(query, location)

                    if results:
                        output_title = f"<h3 style='color: var(--primary);'>🔍 Found {len(results)} results for "
                        if search_mode == "Career Path" and selected_career:
                            output_title += f"<span style='color: var(--secondary);'>{selected_career}</span> role"
                        else:
                            output_title += f"keywords <span style='color: var(--secondary);'>'{query}'</span>"
                        if location:
                            output_title += f" in <span style='color: var(--secondary);'>{location}</span>"
                        output_title += f" on <span style='color: var(--secondary);'>{platform}</span>:</h3>"
                        st.markdown(output_title, unsafe_allow_html=True)

                        for index, job in enumerate(results):
                            st.markdown("""<hr style='border:1px solid var(--secondary)'>""", unsafe_allow_html=True)
                            
                            # Job card container
                            st.markdown(f"""
                            <div style='
                                background-color: var(--card);
                                padding: 1rem;
                                border-radius: 8px;
                                margin-bottom: 1rem;
                            '>
                                <h3 style='color: var(--primary);'>✨ {job.get('title', 'N/A').strip()}</h3>
                                <p><strong>Company:</strong> <code>{job.get('company', 'N/A').strip()}</code></p>
                            """, unsafe_allow_html=True)

                            display_location = job.get('location', 'N/A').strip()
                            if not display_location or display_location.lower() == 'n/a':
                                display_location = location if location else 'N/A'
                            st.markdown(f"<p><strong>Location:</strong> <code>{display_location}</code></p>", unsafe_allow_html=True)

                            if 'salary' in job and job['salary'] and job['salary'] != 'N/A':
                                st.markdown(f"<p>💰 <strong>Salary/Stipend:</strong> <code>{job['salary'].strip()}</code></p>", unsafe_allow_html=True)
                            elif 'stipend' in job and job['stipend'] and job['stipend'] != 'N/A':
                                st.markdown(f"<p>💰 <strong>Stipend:</strong> <code>{job['stipend'].strip()}</code></p>", unsafe_allow_html=True)
                            else:
                                st.markdown("<p>💰 <strong>Salary/Stipend:</strong> <em>Not specified</em></p>", unsafe_allow_html=True)

                            if 'type' in job and job['type']:
                                st.markdown(f"<p><strong>Job Type:</strong> <code>{job.get('type').strip()}</code></p>", unsafe_allow_html=True)
                            if 'tags' in job and job['tags']:
                                tags_str = ", ".join(tag.strip() for tag in job['tags'] if tag.strip())
                                if tags_str:
                                    st.markdown(f"<p><strong>Tags:</strong> <code>{tags_str}</code></p>", unsafe_allow_html=True)

                            link = job.get('link', 'N/A')
                            if link and link != 'N/A':
                                st.markdown(f"""<a href="{link}" target="_blank" style='
                                    background-color: var(--secondary);
                                    color: white;
                                    padding: 0.5rem 1rem;
                                    text-decoration: none;
                                    border-radius: 4px;
                                    display: inline-block;
                                    margin-top: 0.5rem;
                                '>🔗 View Opportunity</a>""", unsafe_allow_html=True)
                            else:
                                st.markdown("<p>💔 <strong>Link:</strong> <em>Not Available</em></p>", unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        output_message = "<div style='color: var(--secondary);'>😔 No matching opportunities found"
                        if search_mode == "Career Path" and selected_career:
                            output_message += f" for the <strong>{selected_career}</strong> role"
                        elif query:
                            output_message += f" for the keywords <strong>'{query}'</strong>"
                        if location:
                            output_message += f" in <strong>{location}</strong>"
                        output_message += f" on <strong>{platform}</strong>.</div>"
                        st.markdown(output_message + " Try refining your search criteria.", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"⚠️ An error occurred while fetching jobs: {str(e)}")
                    st.error("Please try again later or check your search parameters.")

    # Call the main function
    main()

if __name__ == "__main__":
    app()
