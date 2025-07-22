import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import pytesseract

# Optional: Set path to Tesseract if not in system PATH (especially on Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def run_ocr(url):
    ocr_text = ""
    visual_score = 0.0
    screenshot_path = "static/sample_screenshot.png"

    try:
        # ✅ Configure headless browser for screenshot
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1366x768")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Allow full content to load

        # ✅ Save screenshot
        os.makedirs("static", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        driver.quit()

        # ✅ Run OCR with block text assumption (psm 6)
        img = Image.open(screenshot_path)
        raw_text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')

        # ✅ Filter lines to remove garbage characters
        lines = raw_text.split('\n')
        filtered_lines = [
            line.strip()
            for line in lines
            if len(line.strip()) > 4 and any(c.isalnum() for c in line)
        ]
        clean_text = ' '.join(filtered_lines)
        ocr_text = clean_text.strip()

        # ✅ Keyword-based phishing visual detection
        phishing_keywords = [
            "verify", "login", "urgent", "password", "credentials", "security",
            "account", "recovery", "update", "confirm", "bank", "reset", "blocked",
            "expired", "alert", "access", "support", "click here", "your information"
        ]
        matches = [word for word in phishing_keywords if word in ocr_text.lower()]
        if matches:
            visual_score = 1.0

        # ✅ Save OCR text output (for audit/report)
        with open("static/ocr_text_output.txt", "w", encoding="utf-8") as f:
            f.write(ocr_text)

    except Exception as e:
        ocr_text = f"OCR Failed: {str(e)}"
        visual_score = 0.0

    return ocr_text, visual_score
