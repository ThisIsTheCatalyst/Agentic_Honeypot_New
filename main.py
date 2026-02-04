from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


app = FastAPI()

@app.get("/")
def health():
    return {"status": "backend running"}

class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message


@app.post("/api/honeypot")
def honeypot(
    body: HoneypotRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != "dev_key":
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {
        "status": "success",
        "reply": "backend received the message"
    }
