import os
import re
import string
import PyPDF2
from docx import Document
from pdfminer.high_level import extract_text as pdfminer_extract_text
from typing import Dict, List, Any, Optional, Union
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class ResumeParser:
    """Parse different resume formats into text and structured data"""
    
    def __init__(self):
        self.text = ""
        self.file_path = ""
        self.file_type = ""
    
    def parse(self, file_object, file_type):
        """Parse the resume file and return the text content
        
        Args:
            file_object: The uploaded file object
            file_type: The type of file (pdf, docx, etc.)
            
        Returns:
            str: The extracted text from the resume
        """
        self.file_type = file_type.lower()
        
        if self.file_type == 'pdf':
            return self._parse_pdf(file_object)
        elif self.file_type == 'docx':
            return self._parse_docx(file_object)
        elif self.file_type == 'txt':
            return self._parse_txt(file_object)
        else:
            return "Unsupported file format. Please upload a PDF, DOCX, or TXT file."
    
    def _parse_pdf(self, file_object):
        """Extract text from PDF file"""
        try:
            # Try with PyPDF2 first
            pdf_reader = PyPDF2.PdfReader(file_object)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            # If PyPDF2 returns little or no text, try with pdfminer
            if len(text.strip()) < 100:
                # Need to reset the file pointer to the beginning
                file_object.seek(0)
                text = extract_text(file_object)
            
            self.text = text
            return text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"
    
    def _parse_docx(self, file_object):
        """Extract text from DOCX file"""
        try:
            # Using python-docx directly
            doc = docx.Document(file_object)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            self.text = text
            return text
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"
    
    def _parse_txt(self, file_object):
        """Extract text from TXT file"""
        try:
            text = file_object.read().decode('utf-8')
            self.text = text
            return text
        except Exception as e:
            return f"Error parsing TXT: {str(e)}"
    
    def extract_contact_info(self):
        """Extract contact information from resume text"""
        if not self.text:
            return {}
            
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, self.text.lower())
        
        phone_pattern = r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
        phones = re.findall(phone_pattern, self.text)
        
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
        linkedin = re.findall(linkedin_pattern, self.text.lower())
        
        github_pattern = r'github\.com/[a-zA-Z0-9_-]+'
        github = re.findall(github_pattern, self.text.lower())
        
        website_pattern = r'(?:https?://)?(?:[a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z0-9]{2,}'
        websites = re.findall(website_pattern, self.text.lower())
        
        filtered_websites = [site for site in websites if not any(
            keyword in site for keyword in ['linkedin', 'github', '@', 'gmail', 'yahoo', 'hotmail']
        )]
        
        return {
            'email': emails[0] if emails else 'NULL',
            'phone': phones[0] if phones else 'NULL',
            'linkedin': linkedin[0] if linkedin else 'NULL',
            'github': github[0] if github else 'NULL',
            'website': filtered_websites[0] if filtered_websites else 'NULL'
        }
    
    def extract_sections(self):
        """Extract common resume sections using advanced NLP techniques"""
        if not self.text:
            return {}
            
        # Define more comprehensive section patterns with weighted scoring
        section_patterns = {
            'summary': {
                'high_confidence': ['professional summary', 'executive summary', 'career summary', 'summary of qualifications'],
                'medium_confidence': ['profile', 'professional profile', 'about me', 'objective', 'career objective'],
                'low_confidence': ['summary', 'profile', 'about'],
                'indicators': ['years of experience', 'professional with', 'seeking', 'position', 'opportunity'],
                'negative_indicators': ['project summary', 'performance summary']
            },
            'experience': {
                'high_confidence': ['work experience', 'professional experience', 'employment history', 'professional background'],
                'medium_confidence': ['experience', 'work history', 'career history', 'positions held'],
                'low_confidence': ['career', 'professional'],
                'indicators': ['present', 'current', 'company', 'employer', 'position', 'job title', 'responsibilities'],
                'date_pattern': r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*\d{4}\s*[-–—]\s*(present|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})'
            },
            'education': {
                'high_confidence': ['education', 'academic background', 'academic qualifications', 'educational qualifications'],
                'medium_confidence': ['academic history', 'degrees', 'academic achievements', 'qualifications'],
                'low_confidence': ['university', 'college', 'school', 'institute'],
                'indicators': ['degree', 'bachelor', 'master', 'doctorate', 'ph.d', 'mba', 'bsc', 'ba', 'bs', 'ms', 'gpa', 'graduated'],
                'negative_indicators': ['continuing education', 'professional education']
            },
            'skills': {
                'high_confidence': ['technical skills', 'skills', 'core competencies', 'competencies'],
                'medium_confidence': ['skill set', 'areas of expertise', 'expertise', 'proficiencies', 'abilities'],
                'low_confidence': ['technologies', 'tools', 'languages', 'frameworks'],
                'indicators': ['proficient in', 'knowledge of', 'familiar with', 'experienced in', 'worked with'],
                'negative_indicators': ['soft skills', 'personal skills']
            },
            'projects': {
                'high_confidence': ['projects', 'project experience', 'key projects', 'notable projects'],
                'medium_confidence': ['personal projects', 'academic projects', 'professional projects', 'project history'],
                'low_confidence': ['project', 'developed', 'implemented', 'created'],
                'indicators': ['developed', 'built', 'designed', 'implemented', 'created', 'collaborated on'],
                'negative_indicators': ['project manager', 'project lead']
            },
            'certifications': {
                'high_confidence': ['certifications', 'professional certifications', 'certificates', 'licenses'],
                'medium_confidence': ['professional credentials', 'accreditations', 'professional development'],
                'low_confidence': ['certified', 'accredited', 'licensed'],
                'indicators': ['certified', 'certificate in', 'certified in', 'license', 'accredited'],
                'negative_indicators': []
            }
        }
        
        # Create a result dictionary with placeholders for all sections
        result = {section: '' for section in section_patterns.keys()}
        
        # Split text into lines and normalize
        lines = [line.strip() for line in self.text.split('\n')]
        
        # First pass: identify likely section headers by scoring each line
        scored_headers = []
        for i, line in enumerate(lines):
            if not line or len(line) < 3:  # Skip empty or very short lines
                continue
                
            line_lower = line.lower()
            line_scores = {}
            
            # Check for strong visual indicators (all caps, bold, etc.)
            visual_score = 0
            if line_lower == line.upper() and len(line) > 3:  # ALL CAPS
                visual_score += 10
            if line_lower.endswith(':'):  # Ends with colon
                visual_score += 5
            if len(line.split()) <= 3:  # Short phrase (likely a header)
                visual_score += 3
                
            # Score each section
            for section, patterns in section_patterns.items():
                score = 0
                
                # Check high confidence patterns
                for pattern in patterns.get('high_confidence', []):
                    if pattern == line_lower or f'{pattern}:' == line_lower:
                        score += 20  # Exact match
                    elif pattern in line_lower:
                        score += 15  # Contains pattern
                        
                # Check medium confidence patterns
                for pattern in patterns.get('medium_confidence', []):
                    if pattern == line_lower or f'{pattern}:' == line_lower:
                        score += 12  # Exact match
                    elif pattern in line_lower:
                        score += 8   # Contains pattern
                        
                # Check low confidence patterns
                for pattern in patterns.get('low_confidence', []):
                    if pattern == line_lower:
                        score += 5   # Exact match
                    elif pattern in line_lower:
                        score += 3   # Contains pattern
                        
                # Check for section-specific indicators in next few lines
                context_score = 0
                look_ahead = min(i + 5, len(lines))
                context_text = ' '.join(lines[i:look_ahead]).lower()
                
                for indicator in patterns.get('indicators', []):
                    if indicator in context_text:
                        context_score += 2
                        
                # Check for negative indicators
                for neg_indicator in patterns.get('negative_indicators', []):
                    if neg_indicator in line_lower:
                        score -= 10  # Strong negative signal
                    elif neg_indicator in context_text:
                        score -= 5   # Context negative signal
                        
                # Special case for experience section: check for date patterns
                if section == 'experience' and 'date_pattern' in patterns:
                    import re
                    date_pattern = patterns['date_pattern']
                    if re.search(date_pattern, context_text, re.IGNORECASE):
                        context_score += 8  # Strong indicator of work experience
                        
                final_score = score + context_score + visual_score
                if final_score > 0:
                    line_scores[section] = final_score
            
            # If we found any matching sections, record the best match
            if line_scores:
                best_section = max(line_scores.items(), key=lambda x: x[1])
                if best_section[1] >= 10:  # Only consider scores above threshold
                    scored_headers.append((i, best_section[0], best_section[1], line))
        
        # Sort headers by position in document
        scored_headers.sort(key=lambda x: x[0])
        
        # Add a sentinel at the end
        scored_headers.append((len(lines), None, 0, ''))
        
        # Second pass: extract content between identified section headers
        for i in range(len(scored_headers) - 1):
            current_idx, current_section, _, section_header = scored_headers[i]
            next_idx, _, _, _ = scored_headers[i + 1]
            
            # Extract content between this header and the next
            # Include the original header text in the output
            section_content = [section_header]
            section_content.extend(lines[current_idx + 1:next_idx])
            
            # Join the lines and store in result
            if current_section:
                result[current_section] = '\n'.join(filter(None, section_content))
                
        # Post-processing: detect skills that might not be in a dedicated section
        if not result['skills'].strip():
            # Look for skill indicators throughout the document
            skill_indicators = ['proficient in', 'skilled in', 'knowledge of', 'familiar with', 
                               'expertise in', 'experienced with', 'competent in']
            skills_text = []
            
            for line in lines:
                line_lower = line.lower()
                if any(indicator in line_lower for indicator in skill_indicators):
                    skills_text.append(line)
                # Look for bullet lists with technical terms
                elif line.strip().startswith('•') or line.strip().startswith('-'):
                    technical_indicators = ['software', 'programming', 'database', 'framework', 'language', 'tool', 'platform']
                    if any(indicator in line_lower for indicator in technical_indicators):
                        skills_text.append(line)
                        
            if skills_text:
                result['skills'] = '\n'.join(skills_text)
                
        # Check for missing education section - try to find by keywords
        if not result['education'].strip():
            edu_keywords = ['bachelor', 'master', 'degree', 'university', 'college', 'school', 'gpa', 'graduated']
            edu_lines = []
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in edu_keywords):
                    # Get a context window around this line
                    start = max(0, i-1)
                    end = min(len(lines), i+3)
                    edu_lines.extend(lines[start:end])
                    
            if edu_lines:
                result['education'] = '\n'.join(edu_lines)
                
        return result
