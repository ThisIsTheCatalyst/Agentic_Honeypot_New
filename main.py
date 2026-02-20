from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import requests
import os
import logging
import time
from typing import List, Dict, Optional, Union

from session_store import get_session, save_session
from agent.agent import agent_step
from agent.agent import rebuild_state_from_history


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


API_KEY = os.getenv("API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is required")

CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

app = FastAPI(title="Agentic Honeypot API", version="1.0")



class Message(BaseModel):
    sender: str
    text: str
    timestamp: Union[int, str]  # doc: ISO string or epoch ms


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[dict]] = None
    metadata: Optional[Dict] = None


def _infer_scam_type(intelligence: dict) -> str:
    """Infer scenario type from extracted intel (for optional scoring)."""
    links = bool(intelligence.get("phishingLinks"))
    upis = bool(intelligence.get("upiIds"))
    banks = bool(intelligence.get("bankAccounts"))
    if links and not (upis or banks):
        return "phishing"
    if banks:
        return "bank_fraud"
    if upis:
        return "upi_fraud"
    return "generic"


@app.get("/")
def health():
    return {"status": "backend running"}



@app.post("/api/honeypot")
def honeypot(
    body: HoneypotRequest,
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
):
    
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    session_id = body.sessionId
    incoming_text = body.message.text

    session = get_session(session_id)

    if body.metadata:
        session["channel"] = body.metadata.get("channel")
        session["locale"] = body.metadata.get("locale")
        session["language"] = body.metadata.get("language")
   
    if not session.get("messages") and body.conversationHistory:
        rebuild_state_from_history(session, body.conversationHistory)
        session["messages"] = []
        session["intelligence"] = {}
        session["agent_state"] = {}

    for msg in (body.conversationHistory or []):
        if msg.get("sender") == "scammer":
            agent_step(session, msg.get("text", ""))


    
    agent_output = agent_step(session, incoming_text)

   
    save_session(session_id, session)

   
    if agent_output["should_finalize"] and not session.get("finalized", False):
        session["finalized"] = True
        save_session(session_id, session)

        intelligence = session.get("intelligence", {})
        engagement_duration_seconds = int(
            time.time() - session.get("started_at", time.time())
        )
        # Infer scam type for optional scoring (doc: scamType 1 pt optional)
        scam_type = _infer_scam_type(intelligence)
        payload = {
            "sessionId": session_id,
            "scamDetected": session.get("scam_detected", False),
            "totalMessagesExchanged": len(session.get("messages", [])),
            "engagementDurationSeconds": engagement_duration_seconds,
            "extractedIntelligence": {
                "phoneNumbers": intelligence.get("phoneNumbers", []),
                "bankAccounts": intelligence.get("bankAccounts", []),
                "upiIds": intelligence.get("upiIds", []),
                "phishingLinks": intelligence.get("phishingLinks", []),
                "emailAddresses": intelligence.get("emailAddresses", []),
                "caseIds": intelligence.get("caseIds", []),
                "policyNumbers": intelligence.get("policyNumbers", []),
                "orderNumbers": intelligence.get("orderNumbers", []),
            },
            "agentNotes": agent_output["agent_notes"],
            "scamType": scam_type,
            "confidenceLevel": session.get("scam_confidence", 0),
        }

        try:
            requests.post(CALLBACK_URL, json=payload, timeout=5)
            logger.info("Final result callback sent for session %s", session_id)
        except Exception as e:
            logger.error("Callback failed: %s", e)

   
    return {
        "status": "success",
        "reply": agent_output["reply"],
    }



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
