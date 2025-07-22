import requests
import re
from bs4 import BeautifulSoup

def analyze_js(url):
    flags = set()

    suspicious_patterns = [
        r'eval\(', r'atob\(', r'document\.write\(', r'fromCharCode\(',
        r'localStorage', r'sessionStorage', r'canvas\.toDataURL', r'fingerprint', r'keylogger',
        r'addEventListener\(["\']keypress["\']\)'
    ]

    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            content = script.string or script.text or ''
            for pattern in suspicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    flags.add(f"Suspicious JS pattern: {pattern}")
    except Exception as e:
        flags.add("JavaScript analysis failed: " + str(e))

    return list(flags)
