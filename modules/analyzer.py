import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import textstat
import docx

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeAnalyzer:
    """Analyze resume content and extract insights"""
    
    def __init__(self):
        self.resume_text = ""
        self.job_description = ""
        self.tokens = []
        self.stop_words = set(stopwords.words('english'))
        
    def set_resume_text(self, text):
        """Set the resume text for analysis"""
        self.resume_text = text
        # Tokenize and preprocess
        self.tokens = self._preprocess_text(text)
        
    def set_job_description(self, text):
        """Set a job description for comparison analysis"""
        self.job_description = text
        
    def _preprocess_text(self, text):
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        filtered_tokens = [token for token in tokens if token not in self.stop_words]
        
        return filtered_tokens
    
    def extract_skills(self, custom_skills_list=None):
        """Extract skills from resume text
        
        Args:
            custom_skills_list: Optional list of skills to look for
            
        Returns:
            dict: Found skills and their frequencies
        """
        if not self.resume_text:
            return {}
            
        # Default skills list (common technical and soft skills)
        default_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'go', 'rust', 'typescript', 'scala', 'r', 'matlab',
            
            # Web Development
            'html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
            'spring', 'asp.net', 'laravel', 'bootstrap', 'jquery', 'webpack', 'rest api',
            
            # Database
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'nosql', 'redis',
            'firebase', 'dynamodb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',
            'ansible', 'git', 'github', 'bitbucket', 'gitlab', 'devops',
            
            # Data Science
            'data science', 'machine learning', 'deep learning', 'ai', 'artificial intelligence',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv',
            'nlp', 'computer vision', 'data mining', 'data visualization', 'tableau', 'power bi',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'mobile development',
            
            # Soft Skills
            'leadership', 'teamwork', 'communication', 'problem solving', 'analytical',
            'critical thinking', 'time management', 'project management', 'agile', 'scrum'
        ]
        
        skills_to_check = custom_skills_list if custom_skills_list else default_skills
        found_skills = {}
        
        # Convert resume text to lowercase for case-insensitive matching
        resume_lower = self.resume_text.lower()
        
        for skill in skills_to_check:
            # Look for whole word matches (using word boundaries)
            pattern = r'\b' + re.escape(skill) + r'\b'
            matches = re.findall(pattern, resume_lower)
            if matches:
                found_skills[skill] = len(matches)
        
        return found_skills
    
    def get_word_frequency(self, top_n=20):
        """Get the most frequent words in the resume"""
        if not self.tokens:
            return {}
            
        # Count word frequencies
        word_freq = Counter(self.tokens)
        
        # Return top N words
        return dict(word_freq.most_common(top_n))
    
    def calculate_readability(self):
        """Calculate readability metrics for the resume"""
        if not self.resume_text:
            return {}
            
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(self.resume_text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(self.resume_text),
            'smog_index': textstat.smog_index(self.resume_text),
            'coleman_liau_index': textstat.coleman_liau_index(self.resume_text),
            'automated_readability_index': textstat.automated_readability_index(self.resume_text),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(self.resume_text),
            'difficult_words': textstat.difficult_words(self.resume_text),
            'syllable_count': textstat.syllable_count(self.resume_text),
            'lexicon_count': textstat.lexicon_count(self.resume_text, removepunct=True)
        }
    
    def compare_with_job(self):
        """Compare resume with job description"""
        if not self.resume_text or not self.job_description:
            return {}
            
        # Process job description
        job_tokens = self._preprocess_text(self.job_description)
        job_token_set = set(job_tokens)
        
        # Process resume tokens
        resume_token_set = set(self.tokens)
        
        # Find keywords in job description that are missing in the resume
        missing_keywords = job_token_set - resume_token_set
        
        # Find matching keywords
        matching_keywords = job_token_set.intersection(resume_token_set)
        
        # Calculate match percentage
        match_percentage = 0
        if job_token_set:
            match_percentage = (len(matching_keywords) / len(job_token_set)) * 100
        
        return {
            'match_percentage': match_percentage,
            'matching_keywords': list(matching_keywords),
            'missing_keywords': list(missing_keywords)
        }
    
    def generate_improvement_suggestions(self):
        """Generate suggestions to improve the resume"""
        suggestions = []
        
        # Check length
        word_count = len(self.tokens)
        if word_count < 200:
            suggestions.append("Your resume seems quite short. Consider adding more details about your experiences and achievements.")
        elif word_count > 1000:
            suggestions.append("Your resume is quite lengthy. Consider condensing it to highlight the most relevant information.")
        
        # Check contact information
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if not re.search(email_pattern, self.resume_text):
            suggestions.append("No email address detected. Make sure to include your email for potential employers to contact you.")
        
        # Check for action verbs
        action_verbs = ['managed', 'led', 'developed', 'created', 'implemented', 'designed', 
                       'achieved', 'improved', 'increased', 'reduced', 'negotiated', 
                       'coordinated', 'conducted', 'analyzed', 'organized']
        
        found_action_verbs = [verb for verb in action_verbs if verb in self.resume_text.lower()]
        if len(found_action_verbs) < 3:
            suggestions.append("Consider using more action verbs (like 'managed', 'developed', 'implemented') to describe your achievements.")
        
        # Check for quantifiable achievements
        number_pattern = r'\b\d+\b'
        numbers = re.findall(number_pattern, self.resume_text)
        if len(numbers) < 3:
            suggestions.append("Add more quantifiable achievements using numbers (e.g., 'increased sales by 20%', 'managed a team of 5').")
        
        # Readability check
        readability = self.calculate_readability()
        if readability.get('flesch_reading_ease', 0) < 30:
            suggestions.append("Your resume has low readability. Consider using shorter sentences and simpler language.")
        
        return suggestions
