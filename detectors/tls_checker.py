# detectors/tls_checker.py

import ssl
import socket
from urllib.parse import urlparse
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def check_tls(url):
    try:
        hostname = urlparse(url).netloc
        if hostname.startswith("www."):
            hostname = hostname[4:]
        if ":" in hostname:
            hostname = hostname.split(":")[0]

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                cert = x509.load_der_x509_certificate(der_cert, default_backend())
                cert_data = ssock.getpeercert()

        flags = []
        score = 1.0

        # Check expiration
        expiry_date = cert.not_valid_after
        days_left = (expiry_date - datetime.datetime.utcnow()).days
        if days_left < 30:
            flags.append("⚠️ Short-lived certificate (expires in <30 days)")
            score -= 0.3

        # Check issuer
        issuer = cert.issuer.rfc4514_string()
        if "Let's Encrypt" in issuer:
            flags.append("⚠️ Low-assurance issuer: Let's Encrypt")
            score -= 0.2

        # Check SAN (Subject Alternative Names)
        try:
            san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            san_domains = san_extension.value.get_values_for_type(x509.DNSName)
            if hostname not in san_domains:
                flags.append("❌ Domain mismatch in certificate SAN")
                score -= 0.5
        except Exception as e:
            flags.append("⚠️ Could not verify SAN: " + str(e))
            score -= 0.2

        if not flags:
            flags.append("✅ TLS certificate appears valid")

        return {
            "issuer": issuer,
            "valid_days_remaining": days_left,
            "flags": flags,
            "score": round(max(score, 0.0), 2)
        }

    except Exception as e:
        return {
            "issuer": "Unknown",
            "valid_days_remaining": 0,
            "flags": ["❌ TLS check failed: " + str(e)],
            "score": 0.0
        }
