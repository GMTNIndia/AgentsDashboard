from typing import Dict, Any, List, Optional
from crewai_tools import BaseTool
from pydantic import Field
import json
import requests

class JobSkillsAnalysisTool(BaseTool):
    name: str = "Job Skills Analysis Tool"
    description: str = "Analyzes job roles and the skills required for candidates using internet search data."
    api_key: str = Field(default="1ca74486c387cb89ef6fc1387abc69c1baf12fbd")
    serper_url: str = Field(default="https://google.serper.dev/search")
    
    class Config:
        arbitrary_types_allowed = True

    def _run(self, job_role: str, requirements: str = None, provided_description: str = None) -> str:
        if not requirements:
            requirements = self._fetch_job_requirements(job_role)
        job_data = self._run_analysis(job_role, requirements, provided_description)
        return json.dumps(job_data, indent=2)

    def _run_analysis(self, job_role: str, requirements: str, provided_description: str = None) -> Dict[str, Any]:
        skills_list = [skill.strip() for skill in requirements.split(',')]
        job_role_data = self._analyze_job_role(job_role)
        
        analysis_result = {
            'job_role': job_role_data,
            'required_skills': skills_list
        }
        
        if provided_description:
            comparison = self._compare_descriptions(provided_description, job_role_data)
            analysis_result['description_comparison'] = comparison
        
        return analysis_result

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
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error during search request: {e}")
            return {}

    def _extract_job_info(self, results: Dict[str, Any]) -> Dict[str, Any]:
        job_data = {
            'role': 'N/A',
            'key_responsibilities': [],
            'technical_skills': [],
            'non_technical_skills': [],
            'qualifications': [],
            'serper_results': []
        }

        for result in results.get('organic', []):
            snippet = result.get('snippet', '').lower()
            title = result.get('title', '')
            link = result.get('link', '')

            job_data['serper_results'].append({
                'title': title,
                'link': link,
                'snippet': snippet
            })

            if 'responsibilities' in snippet:
                job_data['key_responsibilities'].extend(self._extract_responsibilities(snippet))
            if 'skills' in snippet or 'requirements' in snippet:
                technical, non_technical = self._extract_skills_and_qualifications(snippet)
                job_data['technical_skills'].extend(technical)
                job_data['non_technical_skills'].extend(non_technical)
            if 'qualifications' in snippet:
                job_data['qualifications'].extend(self._extract_qualifications(snippet))

        job_data['key_responsibilities'] = list(set(job_data['key_responsibilities']))
        job_data['technical_skills'] = list(set(job_data['technical_skills']))
        job_data['non_technical_skills'] = list(set(job_data['non_technical_skills']))
        job_data['qualifications'] = list(set(job_data['qualifications']))

        return job_data

    def _extract_responsibilities(self, text: str) -> List[str]:
        responsibilities = []
        lines = text.split('. ')
        for line in lines:
            if 'responsibilities' in line:
                words = line.split()
                responsibilities.extend(word.capitalize() for word in words if word.isalpha() and len(word) > 2)
        return responsibilities

    def _extract_skills_and_qualifications(self, text: str):
        technical_skills = []
        non_technical_skills = []
        lines = text.split('. ')
        for line in lines:
            if 'skills' in line or 'requirements' in line:
                words = line.split()
                if 'technical' in line:
                    technical_skills.extend(word.capitalize() for word in words if word.isalpha())
                else:
                    non_technical_skills.extend(word.capitalize() for word in words if word.isalpha())
        return technical_skills, non_technical_skills

    def _extract_qualifications(self, text: str) -> List[str]:
        qualifications = []
        lines = text.split('. ')
        for line in lines:
            if 'qualifications' in line:
                words = line.split()
                qualifications.extend(word.capitalize() for word in words if word.isalpha() and len(word) > 2)
        return qualifications

    def _analyze_job_role(self, job_role: str) -> Dict[str, Any]:
        search_results = self._search(f"{job_role} job requirements and skills")
        job_data = self._extract_job_info(search_results)
        job_data['role'] = job_role

        return job_data

    def _fetch_job_requirements(self, job_role: str) -> str:
        search_results = self._search(f"{job_role} job requirements")
        requirements = []
        for result in search_results.get('organic', []):
            snippet = result.get('snippet', '').lower()
            requirements.extend(self._extract_requirements(snippet))
        return ', '.join(set(requirements[:5]))

    def _extract_requirements(self, text: str) -> List[str]:
        requirements = []
        lines = text.split('. ')
        for line in lines:
            if 'requirements' in line or 'responsibilities' in line or 'skills' in line:
                words = line.split()
                requirements.extend(word.capitalize() for word in words if word.isalpha() and len(word) > 2)
        return requirements

    def _compare_descriptions(self, provided_description: str, job_role_data: Dict[str, Any]) -> Dict[str, Any]:
        comparison = {
            'provided_description': provided_description,
            'job_role_data': job_role_data,
            'differences': {
                'key_responsibilities': self._find_differences(provided_description, job_role_data.get('key_responsibilities', [])),
                'technical_skills': self._find_differences(provided_description, job_role_data.get('technical_skills', [])),
                'non_technical_skills': self._find_differences(provided_description, job_role_data.get('non_technical_skills', [])),
                'qualifications': self._find_differences(provided_description, job_role_data.get('qualifications', [])),
            }
        }
        return comparison

    def _find_differences(self, provided_description: str, extracted_data: List[str]) -> List[str]:
        differences = []
        for item in extracted_data:
            if item.lower() not in provided_description.lower():
                differences.append(item)
        return differences

    def generate_report(self, job_role: str, requirements: str = None, provided_description: str = None, file_path: str = r'C:\Users\HP\Desktop\jobskill\outs\job_skills_analysis_report_raw.md'):
        """Generate the job skills analysis report."""
        report_data = self._run(job_role, requirements, provided_description)
        with open(file_path, 'w') as file:
            file.write(report_data)
        print(f"Report generated at: {file_path}")
