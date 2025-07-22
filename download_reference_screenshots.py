import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Expanded list of popular reference sites
reference_sites = [
    {"url": "https://github.com/", "filename": "github.png"},
    {"url": "https://www.amazon.com/login", "filename": "amazon_login.png"},
    {"url": "https://www.paypal.com/signin", "filename": "paypal_signin.png"},
    {"url": "https://www.google.com", "filename": "google_home.png"},
    {"url": "https://www.facebook.com/login", "filename": "facebook_login.png"},
    {"url": "https://www.github.com/login", "filename": "github_login.png"},
    {"url": "https://www.linkedin.com/login", "filename": "linkedin_login.png"},
    {"url": "https://www.instagram.com/accounts/login", "filename": "instagram_login.png"},
    {"url": "https://twitter.com/login", "filename": "twitter_login.png"},
    {"url": "https://www.netflix.com/login", "filename": "netflix_login.png"},
    {"url": "https://www.reddit.com/login", "filename": "reddit_login.png"},
    {"url": "https://accounts.google.com/signin", "filename": "google_signin.png"},
    {"url": "https://www.apple.com", "filename": "apple_home.png"},
    {"url": "https://outlook.live.com/owa/", "filename": "outlook_web.png"},
    {"url": "https://web.whatsapp.com", "filename": "whatsapp_web.png"},
    {"url": "https://web.telegram.org", "filename": "telegram_web.png"},
    {"url": "https://mail.yahoo.com", "filename": "yahoo_mail.png"},
    {"url": "https://youtube.com", "filename": "youtube_home.png"}
]

def capture_full_screenshot(url, save_path):
    print(f"🌐 Capturing: {url}")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,5000")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Allow JS content to load
        driver.save_screenshot(save_path)
        driver.quit()
        print(f"✅ Saved to {save_path}")
    except Exception as e:
        print(f"❌ Failed to capture {url}: {e}")

def main():
    ref_folder = "ref"
    os.makedirs(ref_folder, exist_ok=True)

    for site in reference_sites:
        path = os.path.join(ref_folder, site["filename"])
        capture_full_screenshot(site["url"], path)

if __name__ == "__main__":
    main()
