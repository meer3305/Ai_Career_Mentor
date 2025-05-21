# modules/interview_simulator.py

import os
import sys
import json
import re
import random
import textwrap
import traceback

# Add project root (AI_CAREER_MENTOR) to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.groq_openai import client, MODEL  # Your Groq API client wrapper


def load_roles(path="config/job_roles.json"):
    """Load job roles from JSON file or return defaults."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
            # Support roles key or direct list
            return data.get("roles", data) if isinstance(data, dict) else data
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading roles: {e}")
        return ["Software Engineer", "Data Scientist", "Product Manager"]



import re  # make sure this is imported at the top of your file

def generate_mcq_general(role, difficulty, keywords=None):
    """Generate one multiple-choice question in structured dict form."""
    prompt = f"""Generate one multiple-choice question for a General Knowledge for {role} interview at {difficulty} level. Don't repeat any questions. You can give different options for the same question.Make sure there is a varirety of questions. 
Format:
Question: ...
Options:
A. ...
B. ...
C. ...
D. ...
Answer: <Correct Option Letter>
Explanation: ...
"""
    if keywords:
        prompt += f"\nInclude: {', '.join(keywords)}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

        question_match = re.search(r"Question:\s*(.*)", content)
        options = re.findall(r"[A-D]\.\s*([^\n]+)", content)
        answer_letter_match = re.search(r"Answer:\s*([A-D])", content)
        explanation_match = re.search(r"Explanation:\s*(.*)", content, re.DOTALL)

        if not (question_match and options and answer_letter_match and explanation_match):
            raise ValueError("Failed to parse MCQ response.")

        question = question_match.group(1).strip()
        answer_letter = answer_letter_match.group(1).strip()
        explanation = explanation_match.group(1).strip()

        correct_index = ord(answer_letter) - ord("A")
        correct_answer = options[correct_index] if 0 <= correct_index < len(options) else None

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
        }
    except Exception as e:
        return {
            "error": f"❌ Error generating MCQ: {e}",
            "raw_response": content if 'content' in locals() else "No response"
        }


def generate_mcq_dsa(role, difficulty, keywords=None):
    """Generate one multiple-choice question in structured dict form."""
    prompt = f"""Generate one multiple-choice question for DSA/Specialisation Knowledge based on role which is asked in for {role} interview at {difficulty} level. Don't repeat any questions. You can give different options for the same question.Make sure there is a varirety of questions. 
Format:
Question: ...
Options:
A. ...
B. ...
C. ...
D. ...
Answer: <Correct Option Letter>
Explanation: ...
"""
    if keywords:
        prompt += f"\nInclude: {', '.join(keywords)}"

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()

        question_match = re.search(r"Question:\s*(.*)", content)
        options = re.findall(r"[A-D]\.\s*([^\n]+)", content)
        answer_letter_match = re.search(r"Answer:\s*([A-D])", content)
        explanation_match = re.search(r"Explanation:\s*(.*)", content, re.DOTALL)

        if not (question_match and options and answer_letter_match and explanation_match):
            raise ValueError("Failed to parse MCQ response.")

        question = question_match.group(1).strip()
        answer_letter = answer_letter_match.group(1).strip()
        explanation = explanation_match.group(1).strip()

        correct_index = ord(answer_letter) - ord("A")
        correct_answer = options[correct_index] if 0 <= correct_index < len(options) else None

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation,
        }
    except Exception as e:
        return {
            "error": f"❌ Error generating MCQ: {e}",
            "raw_response": content if 'content' in locals() else "No response"
        }

