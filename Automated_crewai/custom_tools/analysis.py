from typing import Dict, Any, List
from crewai_tools import BaseTool
from pydantic import Field
import json
import requests
import re

class CompetitiveAnalysisTool(BaseTool):
    name: str = "Competitive Analysis Tool"
    description: str = "Analyzes a company and its competitors using internet search data."
    api_key: str = Field(default="1ca74486c387cb89ef6fc1387abc69c1baf12fbd")
    serper_url: str = Field(default="https://google.serper.dev/search")

    def _run(self, company_name: str, competitors: str = None) -> str:
        if not competitors:
            competitors = self._fetch_top_competitors(company_name)
        result = self._run_analysis(company_name, competitors)
        return json.dumps(result, indent=2)

    def _run_analysis(self, company_name: str, competitors: str) -> Dict[str, Any]:
        competitor_list = [comp.strip() for comp in competitors.split(',')]
        competitor_data = [self._analyze_company(comp) for comp in competitor_list]
        main_company_data = self._analyze_company(company_name)
        
        return {
            'main_company': main_company_data,
            'competitors': competitor_data
        }

    def _search(self, query: str) -> Dict[str, Any]:
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(self.serper_url, headers=headers, data=payload)
            response.raise_for_status()
            result = response.json()
            print(f"Search results for '{query}': {json.dumps(result, indent=2)}")  # Debug: Print the response
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error during search request: {e}")
            return {}

    def _extract_company_info(self, results: Dict[str, Any]) -> Dict[str, Any]:
        company_data = {
            'name': 'N/A',
            'website': 'N/A',
            'market_cap': 'N/A',
            'revenue': 'N/A',
            'customer_satisfaction': 'N/A',
            'reviews': 'N/A',
            'swot_analysis': {
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'threats': []
            },
            'serper_results': []
        }

        for result in results.get('organic', []):
            snippet = result.get('snippet', '').lower()
            title = result.get('title', '')
            link = result.get('link', '')
            
            company_data['serper_results'].append({
                'title': title,
                'link': link,
                'snippet': snippet
            })
            
            print(f"Snippet: {snippet}")

            if 'market cap' in snippet:
                company_data['market_cap'] = self._extract_value(snippet, r'market cap:?\s*[\$€£]?\d+(\.\d+)?[mbk]?')
            if 'revenue' in snippet:
                company_data['revenue'] = self._extract_value(snippet, r'revenue:?\s*[\$€£]?\d+(\.\d+)?[mbk]?')
            if 'customer satisfaction' in snippet:
                company_data['customer_satisfaction'] = self._extract_value(snippet, r'customer satisfaction:?\s*\d+(\.\d+)?%?')
            if 'review' in snippet:
                company_data['reviews'] = self._extract_value(snippet, r'\d+(\.\d+)? out of \d+(\.\d+)? stars')

            for category in ['strength', 'weakness', 'opportunity', 'threat']:
                if category in snippet:
                    company_data['swot_analysis'][f'{category}s'].append(snippet)

        return company_data

    def _extract_value(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(0) if match else 'N/A'

    def _analyze_company(self, company_name: str) -> Dict[str, Any]:
        search_results = self._search(f"{company_name} company information")
        company_data = self._extract_company_info(search_results)
        company_data['name'] = company_name

        if search_results.get('organic'):
            company_data['website'] = search_results['organic'][0].get('link', 'N/A')

        return company_data

    def _fetch_top_competitors(self, company_name: str) -> str:
        search_results = self._search(f"top competitors of {company_name}")
        competitors = []
        for result in search_results.get('organic', []):
            snippet = result.get('snippet', '').lower()
            competitors.extend(self._extract_competitors(snippet, company_name))
        return ', '.join(set(competitors[:5])) 

    def _extract_competitors(self, text: str, company_name: str) -> List[str]:
        competitors = []
        lines = text.split('. ')
        for line in lines:
            if 'competitors' in line or 'rivals' in line:
                words = line.split()
                for word in words:
                    if word.isalpha() and word.lower() != company_name.lower():
                        competitors.append(word.capitalize())
        return competitors
