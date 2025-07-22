import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Load a pre-trained ML model (or return dummy if not found)
MODEL_PATH = "model/phishing_rf_model.joblib"

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def extract_features(url_features, tls_result, domain_info, nlp_score, js_flags, visual_score, dom_flags):
    return [
        url_features.get("url_entropy", 3.5),
        len(tls_result.get("flags", [])),
        domain_info.get("domain_age_days", 0),
        nlp_score.get("confidence", 0.5),
        visual_score,
        len(js_flags),
        len(dom_flags)
    ]

def predict_phishing(url_features, tls_result, domain_info, nlp_score, js_flags, visual_score, dom_flags):
    features = extract_features(
        url_features, tls_result, domain_info, nlp_score, js_flags, visual_score, dom_flags
    )
    features = np.array(features).reshape(1, -1)
    model = load_model()

    if model:
        pred = model.predict(features)[0]
        score = model.predict_proba(features)[0][1] * 100
        verdict = "Phishing" if pred == 1 else "Legit"
    else:
        # fallback rule-based logic
        flag_count = features[1] + features[5] + features[6]
        score = 95 - (flag_count * 15)
        score = max(0, min(score, 100))
        verdict = "Phishing" if score < 50 else "Legit"

    return round(score, 2), verdict