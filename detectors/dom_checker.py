import requests
from bs4 import BeautifulSoup

def analyze_dom(url):
    flags = []

    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')

        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        iframes = soup.find_all('iframe')

        for form in forms:
            inputs_in_form = form.find_all('input')
            if any('password' in (i.get('type') or '') for i in inputs_in_form):
                if not form.get('action') or 'http' not in form.get('action', ''):
                    flags.append("Suspicious form: missing or relative action")

        for input_tag in inputs:
            style = input_tag.get('style', '')
            if 'display:none' in style or 'visibility:hidden' in style or 'left:-9999px' in style:
                flags.append("Hidden input field detected (possible honeypot)")

        if len(iframes) > 2:
            flags.append("Multiple iframes detected (possible content masking)")

        if len(forms) == 0:
            flags.append("No forms found on a site with login-like behavior")

    except Exception as e:
        flags.append("DOM analysis failed: " + str(e))

    return {"flags": flags}
