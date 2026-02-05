def choose_strategy(session, incoming_text, reflection=None):
    intel = session.get("intelligence", {})
    agent_state = session.get("agent_state", {})

    turns = agent_state.get("turns", 0)

    upis = intel.get("upiIds", [])
    phones = intel.get("phoneNumbers", [])
    links = intel.get("phishingLinks", [])
    banks = intel.get("bankAccounts", [])
    keywords = intel.get("suspiciousKeywords", [])

    text = incoming_text.lower()

    # ---------------------------
    # Reflection-based override
    # ---------------------------
    if reflection == "progress":
        return "delay"

    if reflection == "stall":
        return "extract_identity"

    # ---------------------------
    # OTP / technical scam path
    # ---------------------------
    if "otp" in text and turns < 8:
        return "extract_identity"

    # ---------------------------
    # Payment extraction priority
    # ---------------------------
    if not upis:
        return "extract_payment"

    if upis and not banks and turns < 10:
        return "extract_bank"

    # ---------------------------
    # Phishing / link-based scams
    # ---------------------------
    if links and turns < 10:
        return "delay"

    # ---------------------------
    # Aggression / urgency handling
    # ---------------------------
    if any(k in keywords for k in ["urgent", "final warning", "blocked"]) and turns < 12:
        return "delay"

    # ---------------------------
    # Termination conditions
    # ---------------------------
    if turns >= 15:
        return "terminate"

    return "delay"
