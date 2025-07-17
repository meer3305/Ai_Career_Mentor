import requests
from bs4 import BeautifulSoup
import time
import random
import logging

class JobScraper:
    def __init__(self, source, min_salary=0, max_pages=3, delay_range=(0.5, 1.5)):
        self.source = source.lower()
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.min_salary = min_salary
        self.max_pages = max_pages
        self.delay_range = delay_range
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    def _random_delay(self):
        time.sleep(random.uniform(*self.delay_range))

    def fetch_jobs(self, query, location=None):
        if self.source == "linkedin":
            jobs = self._fetch_linkedin_jobs(query, location)
        elif self.source == "internshala":
            jobs = self._fetch_internshala_jobs(query, location)
        elif self.source == "remotive":
            jobs = self._fetch_remotive_jobs(query)
        else:
            raise ValueError(f"Unsupported platform: {self.source}")
        return self._filter_by_salary(jobs)

    def _fetch_internshala_jobs(self, query, location):
    
        jobs = []
        try:
            for page in range(1, self.max_pages + 1):
                base = f"https://internshala.com/internships/"
                path = f"internship-in-{location.replace(' ', '-')}/" if location else ""
                url = f"{base}{path}keywords-{query.replace(' ', '-')}/page-{page}/"
                logging.info(f"Fetching Internshala page {page}: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.select(".individual_internship")
                if not job_cards:
                    break

                for job_card in job_cards:
                    link = job_card.get("data-href")
                    if not link:
                        view_link = job_card.select_one("a.view_detail_button")
                        link = view_link['href'] if view_link and 'href' in view_link.attrs else "/"

                    # ✅ Fix for job role/title
                    title_elem = job_card.select_one("div.internship_header div.profile")
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"

                    # ✅ Company name
                    company_elem = job_card.select_one("div.company_name a") or job_card.select_one("div.company_name")
                    company = company_elem.text.strip() if company_elem else "N/A"

                    # ✅ Location
                    location_elem = job_card.select_one(".location_link")
                    location_text = location_elem.text.strip() if location_elem else (location or "N/A")

                    # ✅ Stipend
                    stipend_elem = job_card.select_one(".stipend")
                    stipend = stipend_elem.text.strip() if stipend_elem else "N/A"

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "link": "https://internshala.com" + link,
                        "stipend": stipend,
                        "source": "Internshala"
                    })

                self._random_delay()

        except Exception as e:
            logging.error(f"Internshala error: {e}", exc_info=True)

        return jobs



    def _fetch_linkedin_jobs(self, query, location):
        jobs = []
        try:
            for page in range(self.max_pages):
                url = f"https://www.linkedin.com/jobs/search/?keywords={query}&start={page * 25}"
                if location:
                    url += f"&location={location}"
                logging.info(f"Fetching LinkedIn page {page+1}: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.select(".base-card")
                if not job_cards:
                    break

                for job_card in job_cards:
                    jobs.append({
                        "title": job_card.select_one(".base-search-card__title").text.strip() if job_card.select_one(".base-search-card__title") else "N/A",
                        "company": job_card.select_one(".base-search-card__subtitle").text.strip() if job_card.select_one(".base-search-card__subtitle") else "N/A",
                        "location": job_card.select_one(".job-search-card__location").text.strip() if job_card.select_one(".job-search-card__location") else (location or "N/A"),
                        "link": job_card.select_one("a.base-card__full-link")['href'] if job_card.select_one("a.base-card__full-link") else "N/A",
                        "salary": job_card.select_one(".job-search-card__salary-info").text.strip() if job_card.select_one(".job-search-card__salary-info") else "N/A",
                        "source": "LinkedIn"
                    })
                self._random_delay()
        except Exception as e:
            logging.error(f"LinkedIn error: {e}", exc_info=True)
        return jobs

    def _fetch_remotive_jobs(self, query):
        jobs = []
        try:
            url = "https://remotive.io/api/remote-jobs"
            response = requests.get(url, params={"search": query})
            response.raise_for_status()

            for job in response.json().get("jobs", []):
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "location": job.get("candidate_required_location"),
                    "type": job.get("job_type"),
                    "link": job.get("url"),
                    "tags": job.get("tags", []),
                    "salary": job.get("salary", "N/A"),
                    "source": "Remotive"
                })
        except Exception as e:
            logging.error(f"Remotive error: {e}", exc_info=True)
        return jobs


    def _filter_by_salary(self, jobs):
        if self.min_salary <= 0:
            return jobs
        filtered_jobs = []
        for job in jobs:
            salary = job.get("salary", "N/A")
            if isinstance(salary, str) and salary.isdigit():
                salary_value = int(salary)
                if salary_value >= self.min_salary:
                    filtered_jobs.append(job)
            elif isinstance(salary, (int, float)) and salary >= self.min_salary:
                filtered_jobs.append(job)
        return filtered_jobs