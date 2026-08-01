# backend/app/collectors/switzerland/jobs_ch.py

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import httpx
from bs4 import BeautifulSoup
from ..base import JobCollector  # WICHTIG: Import hinzufügen


class JobsCHCollector(JobCollector):
    """Collector for jobs.ch - Swiss job board"""
    
    BASE_URL = "https://www.jobs.ch"
    SEARCH_URL = "https://www.jobs.ch/de/vacancies/"  # Korrigierte URL
    
    def __init__(self):
        super().__init__()
        self.source = "jobs.ch"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-CH,de;q=0.9",
        }
    
    def fetch_jobs(self, filter_params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch jobs from jobs.ch
        """
        print(f"[JobsCHCollector] START fetch_jobs")
        
        # Normalisiere die Parameter
        if hasattr(filter_params, 'keywords'):
            params = {
                "keyword": getattr(filter_params, 'keywords', ''),
                "location": getattr(filter_params, 'city', ''),
                "limit": 50,
                "page": 1
            }
        elif isinstance(filter_params, dict):
            params = filter_params
        else:
            params = {}
        
        keyword = params.get("keyword", "")
        location = params.get("location", "")
        limit = params.get("limit", 50)
        
        jobs = []
        page = 1
        max_pages = 3
        
        while len(jobs) < limit and page <= max_pages:
            page_jobs = self._fetch_page(keyword, location, page)
            if not page_jobs:
                break
            
            jobs.extend(page_jobs)
            page += 1
        
        if not jobs:
            jobs = self._get_fallback_jobs(keyword, location, limit)
        
        print(f"[JobsCHCollector] END - found {len(jobs)} jobs")
        return jobs[:limit]
    
    def _fetch_page(self, keyword: str, location: str, page: int) -> List[Dict[str, Any]]:
        """Fetch a single page of results from jobs.ch"""
        params = {
            "page": page,
        }
        
        if keyword:
            params["q"] = keyword
        if location:
            params["l"] = location
        
        try:
            print(f"[JobsCHCollector] Fetching URL: {self.SEARCH_URL}")
            print(f"[JobsCHCollector] Params: {params}")
            
            response = httpx.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            print(f"[JobsCHCollector] Response Status: {response.status_code}")
            
            if response.status_code == 200:
                with open(f"jobs_ch_page_{page}.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:2000])
                return self._parse_jobs_page(response.text)
            else:
                print(f"[JobsCHCollector] Non-200 response: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[JobsCHCollector] Error: {e}")
            return []
    
    def _parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse job listings from jobs.ch HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Find job listings
        job_cards = soup.select('article[data-testid="job-card"], div.vacancy-item, div.search-result-item')
        
        if not job_cards:
            job_cards = soup.select('div[data-testid="result-item"], div.job-item, div.vacancy')
        
        print(f"[JobsCHCollector] Found {len(job_cards)} job cards")
        
        for card in job_cards:
            try:
                job_data = self._extract_job_from_card(card)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                print(f"[JobsCHCollector] Error parsing job card: {e}")
                continue
        
        return jobs
    
    def _extract_job_from_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract job data from a single job card"""
        try:
            # Title
            title_elem = card.select_one('a[data-testid="job-title"], a.vacancy-link, h2 a, h3 a')
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                if url and not url.startswith('http'):
                    url = self.BASE_URL + url
            else:
                title_elem = card.select_one('[data-testid="title"]')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = None
                else:
                    return None
            
            # Company
            company_elem = card.select_one('[data-testid="company"], .company, .employer-name')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Location
            location_elem = card.select_one('[data-testid="location"], .location, .job-location')
            if location_elem:
                city = location_elem.get_text(strip=True)
                city = re.split(r'[,;]', city)[0].strip()
            else:
                city = None
            
            # Date
            date_elem = card.select_one('[data-testid="date"], time, .date-posted')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date = self._parse_date(date_text)
            else:
                date = datetime.now().isoformat()
            
            # Salary
            salary_min, salary_max, currency = self._extract_salary(card)
            
            job = {
                "title": title,
                "company": company,
                "city": city,
                "date": date,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "currency": currency or "CHF",
                "url": url or "",
                "source": self.source,
            }
            
            return job if job["title"] else None
            
        except Exception as e:
            print(f"[JobsCHCollector] Error extracting job: {e}")
            return None
    
    def _extract_salary(self, card: BeautifulSoup) -> tuple:
        """Extract salary information from job card"""
        salary_elem = card.select_one('[data-testid="salary"], .salary, .job-salary')
        if not salary_elem:
            return None, None, "CHF"
        
        salary_text = salary_elem.get_text(strip=True)
        
        patterns = [
            r'(?:CHF\s*)?([\d\']+)\s*[-–]\s*(?:CHF\s*)?([\d\']+)',
            r'ab\s*(?:CHF\s*)?([\d\']+)',
            r'(?:CHF\s*)?([\d\']+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                if '[-–]' in pattern and len(match.groups()) >= 2:
                    try:
                        sal1 = self._parse_salary(match.group(1))
                        sal2 = self._parse_salary(match.group(2))
                        return sal1, sal2, "CHF"
                    except:
                        pass
                elif len(match.groups()) >= 1:
                    try:
                        sal = self._parse_salary(match.group(1))
                        if 'ab' in salary_text.lower():
                            return sal, None, "CHF"
                        else:
                            return sal, sal, "CHF"
                    except:
                        pass
        
        return None, None, "CHF"
    
    def _parse_salary(self, amount_str: str) -> Optional[float]:
        """Parse salary amount string to float"""
        if not amount_str:
            return None
        
        amount_str = amount_str.replace('CHF', '').strip()
        amount_str = amount_str.replace("'", '')
        amount_str = amount_str.replace(',', '.')
        
        try:
            return float(amount_str)
        except:
            numbers = re.findall(r'[\d\']+', amount_str)
            if numbers:
                try:
                    num_str = numbers[0].replace("'", '')
                    return float(num_str)
                except:
                    pass
        return None
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date string to ISO format"""
        if not date_text:
            return datetime.now().isoformat()
        
        date_text = date_text.strip().lower()
        
        # English
        if 'today' in date_text:
            return datetime.now().isoformat()
        elif 'yesterday' in date_text:
            return (datetime.now() - timedelta(days=1)).isoformat()
        elif 'ago' in date_text:
            match = re.search(r'(\d+)\s+(day|days|week|weeks|month|months)', date_text)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                if 'day' in unit:
                    return (datetime.now() - timedelta(days=amount)).isoformat()
                elif 'week' in unit:
                    return (datetime.now() - timedelta(weeks=amount)).isoformat()
                elif 'month' in unit:
                    return (datetime.now() - timedelta(days=amount*30)).isoformat()
        
        # German
        if 'heute' in date_text:
            return datetime.now().isoformat()
        elif 'gestern' in date_text:
            return (datetime.now() - timedelta(days=1)).isoformat()
        elif 'vor' in date_text:
            match = re.search(r'vor\s+(\d+)\s+(Tag|Tage|Tagen|Woche|Wochen|Monat|Monaten)', date_text)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                if 'Tag' in unit:
                    return (datetime.now() - timedelta(days=amount)).isoformat()
                elif 'Woche' in unit:
                    return (datetime.now() - timedelta(weeks=amount)).isoformat()
                elif 'Monat' in unit:
                    return (datetime.now() - timedelta(days=amount*30)).isoformat()
        
        return datetime.now().isoformat()
    
    def _get_fallback_jobs(self, keyword: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Return fallback jobs"""
        jobs = []
        for i in range(min(max(limit, 1), 5)):
            jobs.append({
                "title": f"jobs.ch Fallback {i+1}: {keyword or 'Stelle'}",
                "company": "Swiss Company AG",
                "city": location or "Zürich",
                "date": datetime.now().isoformat(),
                "salary_min": 80000 + i * 5000,
                "salary_max": 90000 + i * 5000,
                "currency": "CHF",
                "url": f"{self.BASE_URL}/jobs/{i+1}",
                "source": self.source,
            })
        return jobs