import json

def load_career_profiles(path='config/career_profiles.json'):
    with open(path, 'r') as file:
        return json.load(file)

def analyze_skill_gap(user_skills, desired_career, profiles):
    # Normalize skills
    ideal_skills = set(skill.lower() for skill in profiles.get(desired_career, []))
    user_skills = set(skill.lower() for skill in user_skills)

    matched_skills = user_skills.intersection(ideal_skills)
    missing_skills = ideal_skills - matched_skills

    return {
        "ideal_skills": list(ideal_skills),
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "course_suggestions": recommend_courses(missing_skills)
    }

def recommend_courses(missing_skills):
    return {
        skill: f"https://www.udemy.com/s/{skill.replace(' ', '-')}/"
        for skill in missing_skills
    }
# This function generates course URLs based on missing skills.
# This function is a placeholder. In a real-world scenario, you would query a database or an API to get actual course recommendations.
# The course URLs are just examples and may not lead to actual courses.
# In a real-world scenario, you would query a database or an API to get actual course recommendations.

# Example usage:
# if __name__ == "__main__":
#     profiles = load_career_profiles()
#     user_skills = ["Python", "HTML", "SQL"]
#     desired_career = "Full Stack Developer"

#     result = analyze_skill_gap(user_skills, desired_career, profiles)
#     print(json.dumps(result, indent=2))
