import os
import json
from dotenv import load_dotenv
import openai
from groq import Groq

# Load environment
load_dotenv()

# GROQ API config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
openai.api_key = GROQ_API_KEY
openai.api_base = "https://api.groq.com/openai/v1"

# Best model for structured Q&A
GROQ_MODEL = "mixtral-8x7b-32768"
LLAMA_MODEL = "llama3-8b-8192"

# Load job roles from JSON
def load_roles(path="config/job_roles.json"):
    with open(path, "r") as f:
        return json.load(f)

# --- 1. Generate MCQs (Groq Mixtral)
def generate_mcqs(role, difficulty, count=3, keywords=None):
    prompt = f"""
Generate {count} MCQ interview questions for the role '{role}' with {difficulty.lower()} difficulty.
Format:
Q: <question>
A. Option A
B. Option B
C. Option C
D. Option D
Answer: <Correct Option>
Explanation: <Why it's correct>
"""
    if keywords:
        prompt += f"\nFocus on topics: {', '.join(keywords)}."

    response = openai.ChatCompletion.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

# --- 2. Generate single MCQ (if needed individually)
def generate_mcq(role, difficulty, keywords=None):
    prompt = f"""Generate a {difficulty} MCQ interview question for the role '{role}'.
Include 4 options and the correct answer. Format:
Question: ...
Options:
A) ...
B) ...
C) ...
D) ...
Correct Answer: ...
"""
    if keywords:
        prompt += f"\nInclude keywords: {', '.join(keywords)}"

    response = openai.ChatCompletion.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# --- 3. Fill-in-the-blank Question
def generate_fill_in(role, difficulty):
    prompt = f"""Create a single fill-in-the-blank type question for an interview for the role '{role}' at {difficulty.lower()} level."""
    response = openai.ChatCompletion.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# --- 4. DSA/Logic Puzzle (Gamified)
def generate_dsa_puzzle(role):
    prompt = f"""
You're an interviewer. Create an engaging, gamified DSA or logic question for a '{role}' candidate.
Include at least 1 hint.
Format:
Question: ...
Hint: ...
"""
    response = openai.ChatCompletion.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# --- 5. Evaluate Answer (returns feedback + score)
def evaluate_answer(answer, role, difficulty):
    prompt = f"""You are a strict technical interviewer.
Evaluate this candidate's answer for a '{role}' interview at '{difficulty}' level.

Answer: {answer}

Return:
1. Feedback (1-2 lines)
2. Score out of 10
"""
    response = openai.ChatCompletion.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response["choices"][0]["message"]["content"]
# --- 6. Generate Question (for interview simulator)