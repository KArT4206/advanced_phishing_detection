from transformers import pipeline

# Load a lightweight BERT model from HuggingFace (once at start)
classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection")

def detect_phishing_intent(page_text):
    try:
        # Clean input (you can enhance this)
        text = page_text.strip().replace("\n", " ")
        result = classifier(text[:512])  # Limit input to 512 tokens
        label = result[0]["label"]
        score = round(result[0]["score"], 4)

        if label == "spam":
            return {
                "intent": "phishing",
                "confidence": score,
                "trigger": "BERT classified intent as phishing"
            }
        else:
            return {
                "intent": "safe",
                "confidence": score,
                "trigger": "BERT classified intent as benign"
            }
    except Exception as e:
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "trigger": "NLP error: " + str(e)
        }
