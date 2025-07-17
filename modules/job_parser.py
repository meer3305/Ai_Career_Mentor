import re

class JobDataParser:
    @staticmethod
    def parse_salary(raw_salary):
        if not raw_salary or raw_salary == "N/A":
            return 0

        raw_salary = raw_salary.replace(",", "")
        matches = re.findall(r"\d{3,6}", raw_salary)
        if matches:
            numbers = list(map(int, matches))
            return sum(numbers) // len(numbers)  # average if range
        return 0

    @staticmethod
    def normalize_location(location_text):
        return location_text.strip().title() if location_text else "N/A"

    @staticmethod
    def clean_text(text):
        return text.strip() if text else "N/A"

    @staticmethod
    def is_relevant_job(title, query):
        return query.lower() in title.lower()

    @staticmethod
    def extract_job_data(source, job_dict, query):
        # Filters out irrelevant jobs here if needed
        job_dict["relevant"] = JobDataParser.is_relevant_job(job_dict.get("title", ""), query)
        job_dict["salary_amount"] = JobDataParser.parse_salary(
            job_dict.get("stipend") or job_dict.get("salary") or ""
        )
        job_dict["location"] = JobDataParser.normalize_location(job_dict.get("location"))
        job_dict["company"] = JobDataParser.clean_text(job_dict.get("company"))
        job_dict["title"] = JobDataParser.clean_text(job_dict.get("title"))
        return job_dict
