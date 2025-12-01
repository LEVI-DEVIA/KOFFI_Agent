"""
Modèles Pydantic pour l'API
"""
from pydantic import BaseModel
from typing import List, Dict, Any


class Message(BaseModel):
    role: str
    content: str
    id: str = None


class ChatRequest(BaseModel):
    messages: List[Message] = None
    threadId: str = None
    runId: str = None
    state: Dict[str, Any] = {}
    tools: List[Any] = []
    context: List[Any] = []
    forwardedProps: Dict[str, Any] = {}
    stream: bool = False


class ChatResponse(BaseModel):
    message: Message
    metadata: Dict[str, Any]
