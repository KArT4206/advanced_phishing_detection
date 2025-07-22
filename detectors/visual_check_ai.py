import os
import time
import torch
from PIL import Image
from urllib.parse import urlparse
from transformers import CLIPProcessor, CLIPModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- 🔁 Load CLIP Model
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

# --- 🧭 Reference Sites
reference_sites = [
    {"url": "https://www.amazon.com/login", "image": "ref/amazon_login.png"},
    {"url": "https://www.paypal.com/signin", "image": "ref/paypal_signin.png"},
    {"url": "https://www.google.com", "image": "ref/google_home.png"},
    {"url": "https://accounts.google.com/signin", "image": "ref/google_signin.png"},
    {"url": "https://www.facebook.com/login", "image": "ref/facebook_login.png"},
    {"url": "https://github.com/login", "image": "ref/github_login.png"},
    {"url": "https://github.com/", "image": "ref/github.png"},
    {"url": "https://www.linkedin.com/login", "image": "ref/linkedin_login.png"},
    {"url": "https://www.instagram.com/accounts/login", "image": "ref/instagram_login.png"},
    {"url": "https://twitter.com/login", "image": "ref/twitter_login.png"},
    {"url": "https://www.apple.com", "image": "ref/apple_home.png"},
    {"url": "https://www.youtube.com", "image": "ref/youtube_home.png"},
    {"url": "https://youtube.com", "image": "ref/youtube_home.png"},
    {"url": "https://www.netflix.com/login", "image": "ref/netflix_login.png"},
    {"url": "https://www.reddit.com/login", "image": "ref/reddit_login.png"},
    {"url": "https://outlook.live.com/owa/", "image": "ref/outlook_web.png"},
    {"url": "https://web.whatsapp.com", "image": "ref/whatsapp_web.png"},
    {"url": "https://web.telegram.org", "image": "ref/telegram_web.png"},
    {"url": "https://mail.yahoo.com", "image": "ref/yahoo_mail.png"}
]


# --- 🧠 Precompute Reference Embeddings
reference_embeddings = []
for site in reference_sites:
    try:
        img = Image.open(site["image"]).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            emb = clip_model.get_image_features(**inputs)
            emb = emb / emb.norm(dim=-1, keepdim=True)

        # Get domain name as brand
        domain = urlparse(site["url"]).hostname or ""
        brand_name = domain.replace("www.", "").split(".")[0].capitalize()
        reference_embeddings.append((brand_name, emb))

    except Exception as e:
        print(f"⚠️ Could not load reference image {site['image']}: {e}")

# --- 📸 Capture Screenshot
def take_fullpage_screenshot(url, save_path="static/scan.png"):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1400,4000")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(4)
        height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1400, height + 100)
        driver.save_screenshot(save_path)
        driver.quit()
        return save_path
    except Exception as e:
        raise RuntimeError(f"Screenshot failed: {e}")

# --- 🔍 Compare Visual Similarity
def compare_visuals(url):
    flags = []
    matched_brand = "None"
    visual_score = 0.0
    screenshot_path = "static/scan.png"

    try:
        print(f"📸 Capturing: {url}")
        take_fullpage_screenshot(url, screenshot_path)

        screenshot = Image.open(screenshot_path).convert("RGB")
        inputs = clip_processor(images=screenshot, return_tensors="pt")
        with torch.no_grad():
            screenshot_emb = clip_model.get_image_features(**inputs)
            screenshot_emb = screenshot_emb / screenshot_emb.norm(dim=-1, keepdim=True)

        similarities = []
        for ref_brand, ref_emb in reference_embeddings:
            score = torch.nn.functional.cosine_similarity(screenshot_emb, ref_emb).item()
            score = max(0.0, min(score, 1.0))  # Clamp score for safety
            similarities.append((ref_brand, score))

        similarities.sort(key=lambda x: x[1], reverse=True)
        matched_brand, visual_score = similarities[0]

        # --- Flag based on threshold
        percent_score = round(visual_score * 100, 2)
        if visual_score >= 0.85:
            flags.append(f"🚨 Screenshot closely resembles: {matched_brand} ({percent_score}%)")
        elif visual_score >= 0.65:
            flags.append(f"⚠️ Possibly resembles: {matched_brand} ({percent_score}%)")
        else:
            flags.append("✅ No strong visual resemblance to known sites")

    except Exception as e:
        flags.append(f"❌ AI Visual check failed: {str(e)}")

    return {
        "flags": flags,
        "visual_score": round(visual_score * 100, 2),
        "matched_brand": matched_brand,
        "screenshot_path": screenshot_path
    }

# --- 🧪 Manual Test
if __name__ == "__main__":
    test_url = input("Enter URL to test: ").strip()
    result = compare_visuals(test_url)

    print("\n🧠 Visual Detection Result")
    print("-" * 40)
    print(f"Matched Site        : {result['matched_brand']}")
    print(f"Visual Trust Score  : {result['visual_score']}%")
    for flag in result["flags"]:
        print(" -", flag)
