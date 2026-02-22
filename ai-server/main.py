"""
Scan2Home AI Server — FastAPI microservice wrapping the LangChain chatbot agent.
"""
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agent import user_chatbot, agent_chatbot

app = FastAPI(title="Scan2Home AI Server", version="1.0.0")

# ── Default FAQ Context ──────────────────────────────────────────────────────
DEFAULT_FAQ = """
Q: What is Scan2Home?
A: Scan2Home is a QR-driven real estate platform that connects property buyers with agents.

Q: How do I schedule a property viewing?
A: You can request a viewing through the property details page by selecting a date and time slot.

Q: How does the QR code work?
A: Each property has a unique QR code. Scanning it with your phone takes you directly to the property listing.

Q: Can I make an offer online?
A: Yes, you can submit offers directly through the app. The agent will review and may accept, reject, or counter your offer.

Q: How do I contact support?
A: You can reach our support team via the in-app support feature or email support@scan2home.com.
"""


# ── Request / Response Models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: str = ""
    chat_history: Optional[List[Dict[str, str]]] = []
    mode: str = "user"  # "user" or "agent"
    agent_profile: Optional[str] = None
    faq_context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-server"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Unified chat endpoint.
    - mode="user"  → uses user_chatbot (FAQ-based support)
    - mode="agent" → uses agent_chatbot (custom agent persona)
    """
    faq = req.faq_context or DEFAULT_FAQ
    history = req.chat_history or []

    try:
        if req.mode == "agent" and req.agent_profile:
            reply = agent_chatbot(
                full_profile=req.agent_profile,
                chat_history=history,
                FAQ_context=faq,
                message=req.message,
            )
        else:
            reply = user_chatbot(
                FAQ_context=faq,
                chat_history=history,
                message=req.message,
            )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")
