import re

def dedup_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "blocked", "suspended", "freeze", "frozen",
    "account block", "account blocked", "kyc", "immediately",
    "last warning", "final warning", "limited time", "otp",
    "security", "unauthorized", "fraud", "suspicious activity"
]

def extract_intelligence(text: str):
    text_lower = text.lower()

    return {
        # UPI IDs (strict)
        "upiIds": re.findall(
            r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b",
            text
        ),

        # Phone numbers (India-aware)
        "phoneNumbers": re.findall(
            r"(?:\+91[-\s]?)?[6-9]\d{9}",
            text
        ),

        # Phishing / suspicious links
        "phishingLinks": re.findall(
            r"https?://[^\s]+",
            text
        ),

        # Bank account numbers (masked or numeric)
        "bankAccounts": re.findall(
            r"(?:\b\d{9,18}\b|\bXXXX[-\s]?XXXX[-\s]?XXXX\b)",
            text
        ),

        # Suspicious keywords (normalized)
        "suspiciousKeywords": [
            kw for kw in SUSPICIOUS_KEYWORDS
            if kw in text_lower
        ]
    }
