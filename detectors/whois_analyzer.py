# detectors/whois_analyzer.py

import whois
import datetime
import dns.resolver
from urllib.parse import urlparse

def analyze_domain(url):
    result = {
        "domain": None,
        "domain_age_days": 0,
        "flags": [],
        "warnings": [],
    }

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        result["domain"] = domain

        # WHOIS Lookup
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if creation_date:
                domain_age = (datetime.datetime.utcnow() - creation_date).days
                result["domain_age_days"] = domain_age
                if domain_age < 180:
                    result["flags"].append("Very new domain (<6 months old)")
            else:
                result["flags"].append("Creation date missing")
        except Exception as e:
            result["flags"].append("WHOIS failed")
            result["warnings"].append(str(e))

        # Registrar
        try:
            if w.registrar and 'godaddy' in str(w.registrar).lower():
                result["flags"].append("Common phishing registrar: GoDaddy")
        except:
            pass

        # Email Records (soft warnings only)
        def safe_txt_lookup(query):
            try:
                return [r.to_text() for r in dns.resolver.resolve(query, 'TXT')]
            except:
                return []

        # SPF
        spf_records = safe_txt_lookup(domain)
        if not any("v=spf1" in rec.lower() for rec in spf_records):
            result["warnings"].append("No SPF record")

        # DMARC
        dmarc_records = safe_txt_lookup(f"_dmarc.{domain}")
        if not any("v=dmarc1" in rec.lower() for rec in dmarc_records):
            result["warnings"].append("No DMARC record")

        # DKIM (multiple selectors)
        dkim_found = False
        for selector in ["default", "google", "selector", "s1", "s1024"]:
            dkim_records = safe_txt_lookup(f"{selector}._domainkey.{domain}")
            if dkim_records:
                dkim_found = True
                break
        if not dkim_found:
            result["warnings"].append("No DKIM record")

    except Exception as e:
        result["flags"].append("Fatal error: " + str(e))
        result["domain"] = "Unknown"

    return result
