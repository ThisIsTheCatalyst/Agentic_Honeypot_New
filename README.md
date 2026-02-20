# Honeypot API

## Description

This is an **agentic honeypot** that engages scammer messages over multiple turns, extracts actionable intelligence (payment details, links, contacts), and detects scams using a confidence-based scoring model. The agent behaves like a confused, cautious Indian user (English/Hinglish), asks clarifying questions, and avoids sounding suspicious while prolonging the conversation until enough intel is gathered or termination conditions are met. When the conversation ends, a final output is submitted to the evaluator callback with `scamDetected`, `extractedIntelligence`, and `agentNotes`.

## Tech Stack

- **Language:** Python 3
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Storage:** Redis (session state, TTL 1 hour)
- **Key libraries:** Pydantic, python-dotenv, requests
- **LLM/AI:** Google Gemini (Gemini 2.5 Flash) for natural replies when allowed by rate/gating logic; fallback to curated templates in English and Hinglish

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Agentic_Honeypot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or use a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   - `REDIS_URL` – Redis connection URL (required)
   - `API_KEY` – Secret for `x-api-key` header (required for `/api/honeypot`)
   - `GEMINI_API_KEY` – Google AI API key for Gemini
   - `PORT` – Optional; default `8000`

   Example `.env`:
   ```
   REDIS_URL=redis://localhost:6379/0
   API_KEY=your-api-key
   GEMINI_API_KEY=your-gemini-key
   PORT=8000
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   Or: `python main.py`

## API Endpoint

- **URL:** `https://agentichoneypot-production-954c.up.railway.app/api/honeypot`
- **Method:** POST
- **Authentication:** `x-api-key` header (value must match `API_KEY`)

**Response (200):**
```json
{
  "status": "success",
  "reply": "Your honeypot's response to the scammer"
}
```

Health check: `GET /` returns `{"status": "backend running"}`.

## Approach

### How we detect scams

- **Confidence scoring:** Each turn can add to `scam_confidence` based on observed signals (each type counted once per session):
  - UPI IDs shared → +3  
  - Phishing links → +3  
  - Bank account numbers → +3  
  - Phone numbers → +2  
  - Suspicious keywords (e.g. urgent, blocked, OTP, KYC) → up to +2  
  - Urgency language → +2  
  - Financial lure phrases (e.g. “guaranteed return”, “double money”) → +2  
- **Instant detection:** Phrases like “share OTP”, “transfer immediately” set `scam_detected = true` immediately.  
- **Threshold:** When `scam_confidence >= 4`, the session is marked `scam_detected` and never reverted.  
- Scam status is updated on every scammer message and used for termination and callback.

### How we extract intelligence

- **Regex and context-based extraction** on each scammer message:
  - **UPI IDs:** `name@bank`-style patterns  
  - **Phishing links:** `http://` / `https://` URLs  
  - **Phone numbers:** Indian mobile (e.g. +91 prefix, 10-digit 6–9) and context words (call, WhatsApp, etc.)  
  - **Bank accounts:** 8–18 digit numbers near words like “account”, “bank”, “transfer”, “IFSC”  
  - **Email addresses:** Standard email pattern (with TLD to avoid overlapping UPI)  
  - **Suspicious keywords:** Fixed list (urgent, verify, blocked, OTP, KYC, etc.)  
- All extracted items are deduplicated and stored in session `intelligence` and included in the final callback under `extractedIntelligence`.

### How we maintain engagement

- **Strategy selection:** Each turn chooses a strategy (e.g. `delay`, `extract_payment`, `extract_identity`, `extract_bank`, `terminate`) from conversation state, existing intel, and reflection (progress vs stall).  
- **Reflection:** Compares intel before/after the last reply; “progress” → continue with delay, “stall” → switch to identity/payment extraction.  
- **Reply generation:**  
  - **LLM (Gemini):** Used under gating (e.g. first turns, high-value strategies, periodic refresh), with a cap (e.g. 12 calls per session). Prompt instructs a “normal Indian person”, confused and cautious, with language choice (English vs Hinglish) and strict JSON `{ "language", "reply" }`.  
  - **Templates:** Curated English and Hinglish lines per strategy when LLM is not used, with avoidance of recently used lines.  
- **Termination:** We finalize and submit when: scam is detected, minimum turns (e.g. 10) are met, and either we have at least one extracted item, or we’ve stalled several times, or we hit a turn cap (e.g. 20).  
- **Session state:** Stored in Redis (messages, agent_state, intelligence, scam flags, `started_at`) so multi-turn flow and replay from `conversationHistory` work correctly. Final callback includes `engagementDurationSeconds`, `totalMessagesExchanged`, `extractedIntelligence`, and `agentNotes`.
