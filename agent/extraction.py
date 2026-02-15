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

PHONE_CONTEXT = [
    "call", "contact", "whatsapp",
    "mobile", "phone", "reach", "dial"
]

BANK_CONTEXT = [
    "account number", "bank account", "transfer",
    "deposit", "payment", "credited", "send money"
]


def get_context(text, match, window=60):
    pos = text.find(match)
    return text[max(0, pos - window):pos + window].lower()


def extract_intelligence(text: str):
    text_lower = text.lower()

    bank_accounts = []
    upi_ids = []
    phone_numbers = []
    phishing_links = []
    suspicious_keywords = []

    classified_numbers = set()

    # ----------------------
    # UPI IDs
    # ----------------------
    upi_ids = re.findall(
        r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b",
        text
    )

    # ----------------------
    # Links
    # ----------------------
    phishing_links = re.findall(
        r"https?://[^\s]+",
        text
    )

    # ----------------------
    # Numeric candidates
    # ----------------------
    numeric_candidates = re.findall(
        r"\b\d{8,18}\b",
        text
    )

    for number in numeric_candidates:
        if number in classified_numbers:
            continue

        context = get_context(text, number)
        length = len(number)

        # -------- Phone Logic --------
        if (
            length == 10
            and number[0] in "6789"
            and any(word in context for word in PHONE_CONTEXT)
        ):
            phone_numbers.append(number)
            classified_numbers.add(number)
            continue

        # -------- Bank Account Logic --------
        if (
            11 <= length <= 18
            and any(word in context for word in BANK_CONTEXT)
        ):
            bank_accounts.append(number)
            classified_numbers.add(number)
            continue

        # Otherwise ignore numeric (likely reference ID)
        # Since schema does NOT allow referenceNumbers

    # ----------------------
    # Suspicious Keywords
    # ----------------------
    suspicious_keywords = [
        kw for kw in SUSPICIOUS_KEYWORDS
        if kw in text_lower
    ]

    return {
        "bankAccounts": dedup_preserve_order(bank_accounts),
        "upiIds": dedup_preserve_order(upi_ids),
        "phishingLinks": dedup_preserve_order(phishing_links),
        "phoneNumbers": dedup_preserve_order(phone_numbers),
        "suspiciousKeywords": dedup_preserve_order(suspicious_keywords)
    }
