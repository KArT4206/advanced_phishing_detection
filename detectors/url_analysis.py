import math
import re
import requests
from urllib.parse import urlparse

def shannon_entropy(string):
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    entropy = - sum([p * math.log2(p) for p in prob])
    return entropy

def analyze_url(url):
    flags = []
    score = 1.0  # Start with full trust, deduct based on flags

    parsed = urlparse(url)
    path = parsed.path
    hostname = parsed.netloc

    suspicious_keywords = ['login', 'secure', 'account', 'update', 'free', 'bank']
    if any(kw in url.lower() for kw in suspicious_keywords):
        flags.append("⚠️ Suspicious keyword in URL")
        score -= 0.2

    if len(url) > 75:
        flags.append("⚠️ URL length > 75 characters")
        score -= 0.1

    if url.count('/') > 6:
        flags.append("⚠️ URL depth > 6")
        score -= 0.1

    entropy = shannon_entropy(url)
    if entropy > 4.5:
        flags.append("⚠️ High URL entropy (>4.5)")
        score -= 0.2

    redirects = []
    try:
        r = requests.get(url, timeout=5, allow_redirects=True)
        redirects = [resp.url for resp in r.history]
        if len(redirects) > 2:
            flags.append("⚠️ Multiple redirects in URL")
            score -= 0.2
    except:
        flags.append("❌ Failed to resolve redirects")
        score -= 0.1

    if not flags:
        flags.append("✅ URL structure appears normal")

    return {
        "domain": hostname,
        "url_entropy": round(entropy, 3),
        "redirect_chain": redirects,
        "flags": flags,
        "score": round(max(score, 0.0), 2)
    }
