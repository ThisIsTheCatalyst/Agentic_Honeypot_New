import re


def dedup_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_phone(number: str) -> str:
    number = number.replace("+91", "")
    number = number.replace("-", "")
    number = number.replace(" ", "")
    return number.strip()


SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "blocked", "suspended", "freeze", "frozen",
    "account block", "account blocked", "kyc", "immediately",
    "last warning", "final warning", "limited time", "otp",
    "security", "unauthorized", "fraud", "suspicious activity"
]

PHONE_CONTEXT = [
    "call", "contact", "whatsapp", "mobile", "phone", "reach", "dial"
]

BANK_CONTEXT = [
    "account", "a/c", "bank", "transfer", "deposit",
    "credited", "send money", "ifsc"
]


def get_context(text, start, end, window=60):
    return text[max(0, start - window):end + window].lower()


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
    # Email addresses (TLD required to avoid overlapping with UPI IDs)
    # ----------------------
    email_addresses = re.findall(
        r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\.?[a-zA-Z0-9-]*\b",
        text
    )

    # ----------------------
    # Phone Numbers (+91 + local)
    # ----------------------
    phone_matches = re.finditer(
        r"(?:\+91[\-\s]?)?[6-9]\d{9}",
        text
    )

    for match in phone_matches:
        raw_number = match.group()
        normalized = normalize_phone(raw_number)

        phone_numbers.append(normalized)
        classified_numbers.add(normalized)

    # ----------------------
    # Numeric candidates (8–18 digits)
    # ----------------------
    numeric_matches = re.finditer(
        r"\b\d{8,18}\b",
        text
    )

    for match in numeric_matches:
        number = match.group()
        start, end = match.span()
        context = get_context(text, start, end)
        length = len(number)

        normalized = normalize_phone(number)

        if normalized in classified_numbers:
            continue

        # 1️⃣ BANK ACCOUNT FIRST
        if (
            9 <= length <= 18
            and any(word in context for word in BANK_CONTEXT)
        ):
            bank_accounts.append(number)
            classified_numbers.add(normalized)
            continue

        # 2️⃣ PHONE (context-based)
        if (
            length == 10
            and number[0] in "6789"
            and any(word in context for word in PHONE_CONTEXT)
        ):
            phone_numbers.append(normalized)
            classified_numbers.add(normalized)
            continue

        # 3️⃣ Fallback phone
        if length == 10 and number[0] in "6789":
            phone_numbers.append(normalized)
            classified_numbers.add(normalized)

    # ----------------------
    # Suspicious Keywords
    # ----------------------
    suspicious_keywords = [
        kw for kw in SUSPICIOUS_KEYWORDS
        if kw in text_lower
    ]

    # ----------------------
    # Case / Reference IDs (generic: case #, ref:, ticket, etc.)
    # ----------------------
    case_ids = []
    for pattern in [
        r"\b(?:case|ref|reference|ticket|complaint|id)[\s#:]*([a-zA-Z0-9-]{4,})\b",
        r"\b(?:case|ref|reference)[\s#:]*(\d{4,})\b",
    ]:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            case_ids.append(m.group(1).strip())

    # ----------------------
    # Policy numbers
    # ----------------------
    policy_numbers = re.findall(
        r"\bpolicy[\s#:]*(?:no\.?|number)?[\s#:]*([a-zA-Z0-9-]{3,})\b",
        text,
        re.IGNORECASE
    )
    policy_numbers = [p.strip() for p in policy_numbers if len(p.strip()) >= 3]

    # ----------------------
    # Order numbers / Order IDs
    # ----------------------
    order_numbers = re.findall(
        r"\border[\s#:]*(?:id|no\.?|number)?[\s#:]*([a-zA-Z0-9-]{3,})\b",
        text,
        re.IGNORECASE
    )
    order_numbers = [o.strip() for o in order_numbers if len(o.strip()) >= 3]

    return {
        "bankAccounts": dedup_preserve_order(bank_accounts),
        "upiIds": dedup_preserve_order(upi_ids),
        "phishingLinks": dedup_preserve_order(phishing_links),
        "phoneNumbers": dedup_preserve_order(phone_numbers),
        "suspiciousKeywords": dedup_preserve_order(suspicious_keywords),
        "emailAddresses": dedup_preserve_order(email_addresses),
        "caseIds": dedup_preserve_order(case_ids),
        "policyNumbers": dedup_preserve_order(policy_numbers),
        "orderNumbers": dedup_preserve_order(order_numbers),
    }
