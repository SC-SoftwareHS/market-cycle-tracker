#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def debug_pe_scraping():
    """Debug the PE ratio scraping"""
    url = "https://www.multpl.com/s-p-500-pe-ratio"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching from: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Debug: print page title
        title = soup.find('title')
        print(f"Page title: {title.text if title else 'No title found'}")
        
        # Try to find the current value
        selectors = [
            '#current',
            '.current-value',
            '[data-current-value]',
            'div#current',
            'div.metric-value',
            'div.value'
        ]
        
        print("\nTrying selectors:")
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                print(f"  {selector}: {element.get_text().strip()[:50]}")
        
        # Look for any numbers that could be PE ratios
        text = soup.get_text()
        numbers = re.findall(r'(\d{1,3}\.\d{1,2})', text)
        print(f"\nNumbers found on page (first 10): {numbers[:10]}")
        
        # Filter for reasonable PE values
        pe_candidates = [float(n) for n in numbers if 5 <= float(n) <= 50]
        print(f"Potential PE values (5-50 range): {pe_candidates[:5]}")
        
        # Look for text containing "Current" near numbers
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'current' in line.lower() and i < len(lines) - 1:
                print(f"\n'Current' found in line: {line.strip()}")
                print(f"Next line: {lines[i+1].strip() if i+1 < len(lines) else 'N/A'}")
                break
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pe_scraping()