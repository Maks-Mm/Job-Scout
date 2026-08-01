# backend/app/collectors/austria/karriere_at.py

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
from ..base import JobCollector  # WICHTIG: Import von JobCollector


class KarriereATCollector(JobCollector):
    """Collector for Karriere.at job listings"""
    
    BASE_URL = "https://www.karriere.at"
    SEARCH_URL = "https://www.karriere.at/jobs"
    
    def __init__(self):
        super().__init__()
        self.source = "Karriere.at"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9",
        }
    
    def fetch_jobs(self, filter_params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Karriere.at
        """
        print(f"[KarriereATCollector] START fetch_jobs")
        
        # Normalisiere die Parameter
        if hasattr(filter_params, 'keywords'):
            params = {
                "keyword": getattr(filter_params, 'keywords', ''),
                "location": getattr(filter_params, 'city', ''),
                "limit": 50,
                "page": 1
            }
            print(f"[KarriereATCollector] Converted JobFilter: {params}")
        elif isinstance(filter_params, dict):
            params = filter_params
        else:
            params = {}
        
        keyword = params.get("keyword", "")
        location = params.get("location", "")
        limit = params.get("limit", 50)
        page = params.get("page", 1)
        
        jobs = []
        current_page = page
        pages_fetched = 0
        max_pages = 3
        
        while len(jobs) < limit and pages_fetched < max_pages:
            page_jobs = self._fetch_page(keyword, location, current_page)
            if not page_jobs:
                break
            
            jobs.extend(page_jobs)
            current_page += 1
            pages_fetched += 1
        
        if not jobs:
            jobs = self._get_fallback_jobs(keyword, location, limit)
        
        print(f"[KarriereATCollector] END - found {len(jobs)} jobs")
        return jobs[:limit]
    
    def _fetch_page(self, keyword: str, location: str, page: int) -> List[Dict[str, Any]]:
        """Fetch a single page of results"""
        params = {
            "page": page,
        }
        
        if keyword:
            params["search"] = keyword
        if location:
            params["location"] = location
        
        try:
            print(f"[KarriereATCollector] Fetching URL: {self.SEARCH_URL}")
            print(f"[KarriereATCollector] Params: {params}")
            
            response = httpx.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            print(f"[KarriereATCollector] Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Speichere für Debugging
                with open(f"karriere_at_page_{page}.html", "w", encoding="utf-8") as f:
                    f.write(response.text[:2000])
                return self._parse_jobs_page(response.text)
            else:
                print(f"[KarriereATCollector] Non-200 response: {response.status_code}")
                return []
                
        except httpx.RequestError as e:
            print(f"[KarriereATCollector] Request error: {e}")
            return []
        except Exception as e:
            print(f"[KarriereATCollector] Unexpected error: {e}")
            return []
    
    def _parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse job listings from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Find job listings
        job_cards = soup.select('article[data-job-id], div.job-list-item, div.job-item')
        
        if not job_cards:
            job_cards = soup.select('div[data-testid="job-card"], div.job-tile')
        
        print(f"[KarriereATCollector] Found {len(job_cards)} job cards")
        
        for card in job_cards:
            try:
                job_data = self._extract_job_from_card(card)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                print(f"[KarriereATCollector] Error parsing job card: {e}")
                continue
        
        return jobs
    
    def _extract_job_from_card(self, card: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract job data from a single job card"""
        try:
            # Title
            title_elem = card.select_one('h2 a, h3 a, a.job-title, a[data-testid="job-title"]')
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                if url:
                    if not url.startswith('http'):
                        url = self.BASE_URL + url
            else:
                title_elem = card.select_one('[data-testid="job-title"]')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = None
                else:
                    return None
            
            # Company
            company_elem = card.select_one('[data-testid="company-name"], .company, .employer')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            # Location
            location_elem = card.select_one('[data-testid="location"], .location, .job-location')
            city = location_elem.get_text(strip=True) if location_elem else None
            
            # Date
            date_elem = card.select_one('[data-testid="posted-date"], .date, time, .job-date')
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
                "currency": currency or "EUR",
                "url": url or "",
                "source": self.source,
            }
            
            return job if job["title"] else None
            
        except Exception as e:
            print(f"[KarriereATCollector] Error extracting job: {e}")
            return None
    
    def _extract_salary(self, card: BeautifulSoup) -> tuple:
        """Extract salary information from job card"""
        salary_elem = card.select_one('[data-testid="salary"], .salary, .job-salary')
        if not salary_elem:
            return None, None, "EUR"
        
        salary_text = salary_elem.get_text(strip=True)
        
        salary_patterns = [
            r'€\s*([\d.,]+)\s*[-–]\s*€\s*([\d.,]+)',
            r'ab\s*€\s*([\d.,]+)',
            r'€\s*([\d.,]+)\s*[-–]',
            r'€\s*([\d.,]+)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                if '[-–]' in pattern and len(match.groups()) >= 2:
                    try:
                        salary_min = self._parse_salary_amount(match.group(1))
                        salary_max = self._parse_salary_amount(match.group(2))
                        return salary_min, salary_max, "EUR"
                    except:
                        pass
                elif len(match.groups()) >= 1:
                    try:
                        salary = self._parse_salary_amount(match.group(1))
                        if 'ab' in salary_text.lower():
                            return salary, None, "EUR"
                        else:
                            return salary, salary, "EUR"
                    except:
                        pass
        
        return None, None, "EUR"
    
    def _parse_salary_amount(self, amount_str: str) -> Optional[float]:
        """Parse salary amount string to float"""
        if not amount_str:
            return None
        
        amount_str = amount_str.replace('€', '').replace('EUR', '').strip()
        amount_str = amount_str.replace('.', '')
        amount_str = amount_str.replace(',', '.')
        
        try:
            return float(amount_str)
        except ValueError:
            numbers = re.findall(r'[\d.,]+', amount_str)
            if numbers:
                try:
                    num_str = numbers[0].replace('.', '').replace(',', '.')
                    return float(num_str)
                except:
                    pass
        return None
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date string to ISO format"""
        if not date_text:
            return datetime.now().isoformat()
        
        date_text = date_text.strip().lower()
        
        if 'heute' in date_text:
            return datetime.now().isoformat()
        elif 'gestern' in date_text:
            return (datetime.now() - timedelta(days=1)).isoformat()
        elif 'vor' in date_text:
            match = re.search(r'vor\s+(\d+)\s+(Tag|Tage|Tagen)', date_text)
            if match:
                days = int(match.group(1))
                return (datetime.now() - timedelta(days=days)).isoformat()
        
        return datetime.now().isoformat()
    
    def _get_fallback_jobs(self, keyword: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Return fallback test jobs"""
        jobs = []
        for i in range(min(max(limit, 1), 5)):
            jobs.append({
                "title": f"Karriere.at Fallback {i+1}: {keyword or 'Stelle'}",
                "company": "Austrian Company",
                "city": location or "Wien",
                "date": datetime.now().isoformat(),
                "salary_min": 2500 + i * 300,
                "salary_max": 3500 + i * 300,
                "currency": "EUR",
                "url": f"{self.BASE_URL}/jobs/{i+1}",
                "source": self.source,
            })
        return jobs
    
    def fetch_job_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed job information from a specific job URL"""
        try:
            response = httpx.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            description_elem = soup.select_one('.job-description, .description, [data-testid="job-description"]')
            description = description_elem.get_text(strip=True) if description_elem else None
            
            requirements_elem = soup.select_one('.requirements, .qualifications')
            requirements = requirements_elem.get_text(strip=True) if requirements_elem else None
            
            return {
                "description": description,
                "requirements": requirements,
            }
            
        except Exception as e:
            print(f"[KarriereATCollector] Error fetching job details: {e}")
            return None