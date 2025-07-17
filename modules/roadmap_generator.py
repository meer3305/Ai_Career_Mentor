import os

def generate_roadmap(user_skills, desired_career, profiles, api_key=None):
    """
    If the career is in the static mapping (roadmap.sh), return a clean roadmap.sh redirect and optionally the required skills.
    If not, fallback to AI-powered roadmap with free course links for each step.
    """
    # Static mapping for roadmap.sh
    roadmap_sh_slugs = {
        "Frontend Developer": "frontend",
        "Backend Developer": "backend",
        "DevOps Engineer": "devops",
        "Data Scientist": "data-scientist",
        "Full Stack Developer": "full-stack",
        "React Developer": "react",
        "Android Developer": "android",
        "QA Engineer": "qa",
        "Cybersecurity Analyst": "cyber-security",
        "Blockchain Developer": "blockchain",
        "AI/ML Engineer": "ai-data-scientist",
        "Mobile App Developer": "mobile",
        "Web Developer": "frontend",  # or "full-stack" if you prefer
        "Product Manager": "product-management",
        "Business Analyst": "business-analyst",
        # Add more mappings as needed
    }
    if desired_career in roadmap_sh_slugs:
        slug = roadmap_sh_slugs[desired_career]
        roadmap_url = f"https://roadmap.sh/{slug}"
        required_skills = profiles.get(desired_career, [])
        output = f"### Roadmap for {desired_career}\n\n"
        output += f"[View the roadmap on roadmap.sh]({roadmap_url})\n\n"
        if required_skills:
            output += f"**Core Skills:** {', '.join(required_skills)}\n"
        return output

    # --- AI fallback ---
    try:
        from groq import Groq
        from openai import OpenAI
    except ImportError:
        raise ImportError("Please install the 'groq' and 'openai' packages.")

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set. Please provide your API key.")

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    required_skills = profiles.get(desired_career, [])
    prompt = (
        f"You are a career mentor. The user wants to become a '{desired_career}'.\n"
        f"The required skills for this career are: {', '.join(required_skills)}.\n"
        f"The user currently has these skills: {', '.join(user_skills)}.\n"
        "Generate a step-by-step personalized learning roadmap for the user to reach their goal. "
        "For each step, mention the skill/topic, a brief learning suggestion, a practical project idea, and provide a direct link to a high-quality free online course (YouTube, Coursera, edX, or similar) for that skill. "
        "End with a motivational summary. Format the output in markdown."
    )
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    ai_roadmap_text = response.choices[0].message.content
    output = f"### AI-Powered Roadmap for {desired_career}\n\n"
    output += ai_roadmap_text.strip() + "\n"
    return output