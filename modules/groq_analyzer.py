import os
import json
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# --- DummyGroqClient (No changes needed here, it generates valid JSON) ---
class DummyGroqClient:
    """A dummy Groq client for demonstration without a real API key"""

    def create(self, **kwargs):
        messages = kwargs.get('messages', [])
        user_message = next((m['content'] for m in messages if m['role'] == 'user'), '')
        has_job_description = 'JOB DESCRIPTION' in user_message
        dummy_response = {
            "overall_assessment": "This is a dummy analysis generated for demonstration purposes. To get real AI-powered analysis, set the GROQ_API_KEY environment variable.",
            "key_strengths": [
                "Strong structure and organization",
                "Good use of action verbs",
                "Clear presentation of experience"
            ],
            "improvement_areas": [
                "Add more quantifiable achievements",
                "Enhance skills section",
                "Tailor content to target roles"
            ],
            "specific_suggestions": [
                "Include metrics and specific outcomes for your achievements",
                "Add a strong professional summary at the top",
                "Use more industry-specific keywords",
                "Ensure consistent formatting throughout"
            ],
            "structure_feedback": "The resume has a clear structure with defined sections, making it easy to navigate. Consider using more bullet points for better readability.",
            "language_feedback": "The language is professional and concise. You've used some good action verbs, but could incorporate more powerful verbs like 'spearheaded', 'orchestrated', or 'transformed'.",
            "red_flags": [
                "Some job descriptions are too generic",
                "Skills section could be more comprehensive"
            ]
        }

        # Add job comparison if job description was provided
        if has_job_description:
            dummy_response["job_match"] = {
                "match_assessment": "This is a dummy job match assessment. To get a real analysis, please provide a valid Groq API key.",
                "missing_keywords": [
                    "project management",
                    "agile",
                    "scrum",
                    "stakeholder communication",
                    "budget planning"
                ],
                "alignment_score": 65,
                "recommendations": [
                    "Add more keywords from the job description",
                    "Emphasize relevant experience more prominently",
                    "Highlight specific skills requested in the job posting"
                ]
            }

        # Create the response object
        response_obj = type('DummyResponse', (), {})()
        choice_obj = type('DummyChoice', (), {})()
        message_obj = type('DummyMessage', (), {})()

        message_obj.content = json.dumps(dummy_response)
        choice_obj.message = message_obj
        response_obj.choices = [choice_obj]

        return response_obj

    def __init__(self):
        """Initialize the dummy client"""
        pass

# Get API key from environment variable, or None if not set
DEFAULT_API_KEY = os.getenv('GROQ_API_KEY')

class GroqAnalyzer:
    """Interface with Groq API for resume analysis"""

    def __init__(self, api_key: Optional[str] = None):
        # Use provided key, or environment variable, or None
        self.api_key = api_key if api_key else DEFAULT_API_KEY
        self.client = None

        # Only attempt to initialize real client if we have an API key
        if self.api_key:
            self.initialize_client()

        # If no API key or initialization failed, use dummy client
        if self.client is None:
            self.client = DummyGroqClient()
            print("Using demo mode with dummy responses. Set GROQ_API_KEY in .env file for real analysis.")

    def initialize_client(self):
        try:
            import groq
            self.client = groq.Client(api_key=self.api_key).chat.completions
            # Return True to indicate successful initialization
            return True
        except ImportError:
            self.client = DummyGroqClient()
            # Return a message indicating the reason for using dummy client
            return "Error: Groq package not installed. Using dummy client."
        except Exception as e:
            self.client = DummyGroqClient()
            # Return a warning message with the specific error
            return f"Warning: Using dummy Groq client for demonstration. Error: {str(e)}"

    def analyze_resume(self, resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze resume text using Groq API"""
        if self.client is None:
            # Fallback to dummy client if it wasn't initialized (should be handled by __init__)
            self.client = DummyGroqClient()
            print("Warning: Client not initialized, falling back to dummy.")

        try:
            # Define the SYSTEM message with the clear JSON schema
            system_prompt = """You are an expert resume analyzer and career coach. Your task is to provide detailed, professional feedback on a resume in strict JSON format.
            The JSON output must adhere to the following schema:
            {{
              "overall_assessment": "A concise summary of the resume's overall impression and main points.",
              "key_strengths": ["List key strengths, each a concise phrase or sentence."],
              "improvement_areas": ["List main areas for improvement, each a concise phrase or sentence."],
              "specific_suggestions": ["Provide specific, actionable suggestions, each a 1-2 sentence tip."],
              "structure_feedback": "Detailed feedback on the resume's organization, layout, and sectioning.",
              "language_feedback": "Detailed evaluation of the resume's language, tone, action verbs, and conciseness.",
              "red_flags": ["Identify any potential red flags or areas of concern for employers, each a concise phrase or sentence."]
            }}

            If a job description is provided, also include a 'job_match' object within the main JSON, following this nested schema:
            "job_match": {{
                "match_assessment": "An assessment of how well the resume aligns with the job description.",
                "missing_keywords": ["List important keywords from the job description not found or insufficiently emphasized in the resume."],
                "alignment_score": "A number between 0 and 100 representing the alignment score.",
                "recommendations": ["Specific recommendations to tailor the resume to the job description, each a 1-2 sentence tip."]
            }}

            Ensure ALL output is valid JSON, and strictly follow the provided schema. Do not include any additional text outside the JSON object.
            """

            # Define the USER message, providing the data to analyze
            user_prompt = f"""
            RESUME TEXT:
            {resume_text}
            """

            # Append job description to user prompt if provided
            if job_description:
                user_prompt += f"""

                JOB DESCRIPTION:
                {job_description}
                """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Call Groq API
            response = self.client.create(
                model="llama3-70b-8192", # Or your preferred Groq model
                messages=messages,
                temperature=0.3,
                max_tokens=4096,
                response_format={"type": "json_object"} # Crucial for getting JSON output
            )

            analysis_text = response.choices[0].message.content
            return {
                'analysis': analysis_text,
                'error': None
            }

        except Exception as e:
            # It's good to print the raw error for debugging in the console/logs
            print(f"Error calling Groq API: {e}")
            return {
                'analysis': None,
                'error': f"Error analyzing resume with Groq: {str(e)}"
            }

    def generate_ai_suggestions(self, resume_text: str) -> List[str]:
        """Generate specific improvement suggestions for the resume"""
        if isinstance(self.client, DummyGroqClient): # Check if it's the dummy client
            return ["Error: Groq API key not provided. Please set the GROQ_API_KEY environment variable for real AI-powered suggestions."]

        try:
            # Separate system and user prompts for clarity and better control
            system_prompt_suggestions = "You are a highly skilled resume improvement expert. Your sole task is to provide concise, actionable suggestions for a resume."
            user_prompt_suggestions = f"""
            Based on the following resume, provide 5-7 distinct, actionable suggestions for improvement. Focus on clarity, impact, and marketability.
            Present each suggestion as a single, clear sentence.

            RESUME TEXT:
            {resume_text}

            Please provide ONLY the list of suggestions, one per line, without any introductory or concluding remarks.
            """
            
            response = self.client.create(
                model="llama3-8b-8192",  # Using smaller model for faster response
                messages=[
                    {"role": "system", "content": system_prompt_suggestions},
                    {"role": "user", "content": user_prompt_suggestions}
                ],
                temperature=0.4,
                max_tokens=1024
            )

            suggestions_text = response.choices[0].message.content

            # Simple parsing: split by newlines and filter out empty lines
            suggestions = [line.strip().strip('- ') for line in suggestions_text.split('\n') if line.strip()]

            if not suggestions:
                suggestions = ["Unable to generate suggestions. Please try again or provide a more detailed resume."]

            return suggestions

        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]