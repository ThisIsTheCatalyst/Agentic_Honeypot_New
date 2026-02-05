def should_use_llm(strategy: str, agent_state: dict) -> bool:
    turns = agent_state.get("turns", 0)
    llm_calls = agent_state.get("llm_calls", 0)

    # -------------------------------------------------
    # HARD SAFETY CAPS (never break these)
    # -------------------------------------------------
    if llm_calls >= 5:
        return False

    # -------------------------------------------------
    # GUARANTEED REALISM (early hook)
    # -------------------------------------------------
    # Always allow Gemini on first turn
    if turns == 0:
        return True

    # -------------------------------------------------
    # MID-CONVERSATION REALISM REFRESH (Fix #3)
    # -------------------------------------------------
    # One controlled refresh to avoid sounding scripted
    if turns == 4 and llm_calls < 2:
        return True

    # -------------------------------------------------
    # HIGH-VALUE EXTRACTION STRATEGIES
    # -------------------------------------------------
    if strategy in ["extract_payment", "extract_identity", "extract_bank"]:
        return True

    # -------------------------------------------------
    # FINAL REALISM TOUCH (optional, very limited)
    # -------------------------------------------------
    if turns == 8 and llm_calls < 3:
        return True

    # -------------------------------------------------
    # DEFAULT: TEMPLATE FALLBACK
    # -------------------------------------------------
    return False
