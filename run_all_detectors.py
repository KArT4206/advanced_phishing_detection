from urllib.parse import urlparse
from detectors.visual_check_ai import compare_visuals
from detectors import (
    tls_checker,
    whois_analyzer,
    url_analysis,
    ocr_check,
    nlp_intent,
    js_analyzer,
    dom_checker
)

# --- 📊 Adjustable Weights for Each Detector (Total = 100)
DETECTOR_WEIGHTS = {
    "tls": 20,
    "whois": 15,
    "url": 10,
    "js": 25,
    "dom": 10,
    "visual": 10,
    "nlp": 10
}

# --- 🚦 Verdict Thresholds (Editable)
LEGIT_THRESHOLD = 70       # ≥ this score → Legit
UNTRUSTWORTHY_THRESHOLD = 45  # < this → Not Trustworthy
# Between → Potentially Untrustworthy

# --- 🧠 Detector-Specific Thresholds
NLP_SAFE_THRESHOLD = 0.6       # NLP confidence required to consider "safe"
VISUAL_FAIL_THRESHOLD = 0.75   # Visual match > this → suspicious

# --- ✅ Whitelisted Domains
TRUSTED_DOMAINS = [
    "google.com", "facebook.com", "microsoft.com", "amazon.com", "apple.com"
]

def is_whitelisted(url):
    try:
        domain = urlparse(url).hostname or ""
        return any(trusted in domain for trusted in TRUSTED_DOMAINS)
    except:
        return False

# --- 🔍 Main Detector Pipeline
def run_all_detectors(url):
    if is_whitelisted(url):
        return {
            "url": url,
            "trust_score": 99.9,
            "verdict": "Legit",
            "override_reason": "Whitelisted domain",
            "nlp_intent": {"intent": "safe", "confidence": 1.0},
            "ocr_text": "",
            "visual_score": 0.0,
            "matched_brand": "",
            "screenshot_url": "static/sample_screenshot.png",
            "tls_result": {"flags": []},
            "domain_info": {"flags": []},
            "url_features": {"flags": []},
            "js_flags": [],
            "visual_flags": [],
            "dom_flags": [],
            "triggered_checks": ["✅ Domain is whitelisted (trusted source)"]
        }

    # Run all detectors
    tls_result = tls_checker.check_tls(url)
    domain_info = whois_analyzer.analyze_domain(url)
    url_features = url_analysis.analyze_url(url)
    js_flags = js_analyzer.analyze_js(url)
    dom_result = dom_checker.analyze_dom(url)
    visual_result = compare_visuals(url)
    ocr_text, _ = ocr_check.run_ocr(url)
    nlp_result = nlp_intent.detect_phishing_intent(ocr_text)

    visual_score = visual_result["visual_score"] / 100.0
    matched_brand = visual_result["matched_brand"]
    screenshot_path = visual_result["screenshot_path"]
    visual_flags = visual_result["flags"]

    trust_score = 0
    triggered_flags = []

    # Weighted Scoring
    if not tls_result["flags"]:
        trust_score += DETECTOR_WEIGHTS["tls"]
    else:
        triggered_flags += tls_result["flags"]

    if not domain_info["flags"]:
        trust_score += DETECTOR_WEIGHTS["whois"]
    else:
        triggered_flags += domain_info["flags"]

    if not url_features["flags"]:
        trust_score += DETECTOR_WEIGHTS["url"]
    else:
        triggered_flags += url_features["flags"]

    if not js_flags:
        trust_score += DETECTOR_WEIGHTS["js"]
    else:
        triggered_flags += js_flags

    if not dom_result["flags"]:
        trust_score += DETECTOR_WEIGHTS["dom"]
    else:
        triggered_flags += dom_result["flags"]

    if visual_score < VISUAL_FAIL_THRESHOLD:
        trust_score += DETECTOR_WEIGHTS["visual"]
    else:
        triggered_flags += visual_flags

    if nlp_result["intent"] == "safe" and nlp_result["confidence"] >= NLP_SAFE_THRESHOLD:
        trust_score += DETECTOR_WEIGHTS["nlp"]
    else:
        triggered_flags.append(f"⚠️ NLP intent: {nlp_result['intent']} ({nlp_result['confidence']*100:.1f}%)")

    # Final Verdict based on trust score
    if trust_score >= LEGIT_THRESHOLD:
        verdict = "Legit"
    elif trust_score >= UNTRUSTWORTHY_THRESHOLD:
        verdict = "Potentially Untrustworthy"
    else:
        verdict = "Not Trustworthy"

    return {
        "url": url,
        "trust_score": round(trust_score, 2),
        "verdict": verdict,
        "override_reason": "None",
        "triggered_checks": triggered_flags,
        "nlp_intent": nlp_result,
        "ocr_text": ocr_text,
        "visual_score": visual_score * 100,
        "matched_brand": matched_brand,
        "screenshot_url": screenshot_path,
        "tls_result": tls_result,
        "domain_info": domain_info,
        "url_features": url_features,
        "js_flags": js_flags,
        "visual_flags": visual_flags,
        "dom_flags": dom_result["flags"]
    }
