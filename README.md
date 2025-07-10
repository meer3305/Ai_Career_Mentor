The AIML project Made for the CSI Tech Expo 2025

# 🎓 AI-Powered Career Mentor

An intelligent, personalized career guidance platform built with Python and Streamlit.  
It analyzes resumes, detects skill gaps, suggests ideal career paths, provides personalized roadmaps, scrapes relevant courses/jobs, and simulates interviews with AI.

---

## 🚀 Features

- 📄 **Resume Analysis** – Extract and structure your resume content
- 📊 **Skill Gap Detection** – Identify missing skills compared to your dream career
- 🧭 **Roadmap Generator** – Get a step-by-step learning and project plan
- 🌐 **Course/Job Suggestions** – Real-time scraping of internships, jobs, and courses
- 🤖 **AI Interview Simulator** – Practice interviews with an intelligent LLM-powered bot

---

## 🧰 Tech Stack

| Layer        | Toolset                             |
|--------------|-------------------------------------|
| Interface    | Streamlit                           |
| Resume Parsing | PyMuPDF, spaCy, pdfminer.six      |
| AI Models    | OpenAI API, Transformers, scikit-learn |
| Scraping     | BeautifulSoup, requests             |
| Storage      | MongoDB / SQLite                    |
| Deployment   | Streamlit Cloud / Render / Docker   |

---

---

## 📦 Installation

```bash
git clone https://github.com/meer3305/ai_career_mentor.git
cd ai_career_mentor
pip install -r requirements.txt
streamlit run streamlit_app.py




