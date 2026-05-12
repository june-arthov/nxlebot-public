#!/usr/bin/env python3
"""
ScrapeGraph-NXE - Lightweight AI-powered scraper
Created for Nyxelle by Nxe (Raja Hacker AI Assistant)
Uses available tools + LLM for smart extraction
"""

import json
import re
import html
from typing import Optional, Dict, Any, List


class SmartScraper:
    """AI-powered smart scraper - extract data with natural language prompts"""
    
    def __init__(self, prompt: str, source: str):
        self.prompt = prompt
        self.source = source
        self.content = ""
    
    def fetch(self) -> str:
        """Fetch content from URL"""
        # This would use web_fetch tool in actual implementation
        import subprocess
        result = subprocess.run(
            ['curl', '-s', '-A', 'Mozilla/5.0', self.source],
            capture_output=True, text=True, timeout=30
        )
        self.content = result.stdout
        return self.content
    
    def extract(self) -> Dict[str, Any]:
        """Extract data based on prompt using AI analysis"""
        if not self.content:
            self.fetch()
        
        # Simple extraction logic (would use LLM in full version)
        result = {
            "source": self.source,
            "prompt": self.prompt,
            "status": "success",
            "data": self._parse_content()
        }
        return result
    
    def _parse_content(self) -> Dict[str, Any]:
        """Parse HTML content and extract relevant info"""
        data = {}
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', self.content, re.IGNORECASE)
        if title_match:
            data['title'] = title_match.group(1).strip()
        
        # Extract all links
        links = re.findall(r'href=["\']([^"\']+)[\"\']', self.content)
        data['links'] = list(set([l for l in links if l.startswith('http')]))[:50]
        
        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)[\"\']', self.content, re.IGNORECASE)
        if desc_match:
            data['description'] = desc_match.group(1)
        
        # Extract headings
        h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', self.content, re.IGNORECASE)
        data['headings'] = {'h1': [h.strip() for h in h1s]}
        
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', self.content)
        data['emails'] = list(set(emails))
        
        # Extract social media links
        social_patterns = {
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9_.-]+)',
            'linkedin': r'linkedin\.com/(?:in|company)/([a-zA-Z0-9_-]+)',
            'github': r'github\.com/([a-zA-Z0-9_-]+)',
            'instagram': r'instagram\.com/([a-zA-Z0-9_.]+)'
        }
        data['social_media'] = {}
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, self.content)
            if match:
                data['social_media'][platform] = match.group(1)
        
        # Extract forms
        forms = re.findall(r'<form[^>]*>(.*?)</form>', self.content, re.IGNORECASE | re.DOTALL)
        data['forms_count'] = len(forms)
        
        # Extract inputs
        inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', self.content, re.IGNORECASE)
        data['input_fields'] = list(set(inputs))
        
        return data
    
    def run(self) -> Dict[str, Any]:
        """Run the complete scraping pipeline"""
        return self.extract()


class SearchGraph:
    """Multi-page scraper for search results"""
    
    def __init__(self, prompt: str, search_query: str, max_results: int = 5):
        self.prompt = prompt
        self.search_query = search_query
        self.max_results = max_results
    
    def run(self) -> List[Dict[str, Any]]:
        """Search and scrape multiple results"""
        results = []
        # Would use search API here
        return results


def scrape(url: str, prompt: str) -> Dict[str, Any]:
    """Simple one-liner scraping function"""
    scraper = SmartScraper(prompt=prompt, source=url)
    return scraper.run()


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python scrapegraph_nxe.py <url> <prompt>")
        print("Example: python scrapegraph_nxe.py https://example.com 'Extract all links and emails'")
        sys.exit(1)
    
    url = sys.argv[1]
    prompt = sys.argv[2]
    
    result = scrape(url, prompt)
    print(json.dumps(result, indent=2))
