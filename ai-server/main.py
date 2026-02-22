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
A: Scan2Home is an automated real estate platform that uses AI-driven analytics and QR codes to streamline property inventory management and buyer-agent interactions.

Q: How do the QR codes work?
A: Each property is assigned a unique QR code. When a user scans the code, they are instantly directed to the property's digital profile where they can view details, photos, and book viewings.

Q: What does the AI Analytics Module do?
A: The AI module provides automated property analysis and intelligent inventory generation, helping agents extract deep insights from property data without manual entry.

Q: How do I schedule a property viewing?
A: Users can request a viewing directly from the property listing page by selecting an available date and time. The agent will then receive a notification to confirm the booking.

Q: Can I submit a formal offer through the app?
A: Yes, the platform includes an offers module. Users can submit digital offers, and agents can manage them by accepting, rejecting, or sending a counter-offer.

Q: Is my data secure?
A: Yes. Scan2Home uses a hardened production setup where the AI service is isolated in a private Docker network, and all external traffic is secured via SSL/TLS encryption.

Q: How do agents manage their inventory?
A: Agents have access to a dedicated dashboard and management CLI that allows them to track property scans, update listings, and manage automated inventory reports.

Q: What happens if I scan a QR code for a property that is no longer available?
A: The platform will notify you of the property's updated status and suggest similar available listings in the same area.

Q: Does the platform support real-time communication?
A: Yes, Scan2Home features an integrated chat and notification system to ensure seamless communication between agents and prospective buyers.

Q: How do I contact support?
A: You can reach our support team via the in-app support feature or by emailing support@scan2home.com.
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
