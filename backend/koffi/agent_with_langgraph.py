import os
import requests
from typing import List, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_ollama import ChatOllama
from serpapi import GoogleSearch



def extract_content(message):
    """Extrait le contenu texte d'un message LangChain de manière robuste."""
    # Si c'est un objet message LangChain
    if hasattr(message, "content"):
        content = message.content
    else:
        content = message

    # Gérer les différents types de contenu
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extraire uniquement les parties texte
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    text_parts.append(item["text"])
                elif "content" in item:
                    text_parts.append(str(item["content"]))
        return " ".join(text_parts)
    elif isinstance(content, dict):
        if "text" in content:
            return content["text"]
        elif "content" in content:
            return content["content"]
        else:
            return str(content)

    return str(content)


# Chargement des variables d'environnement
load_dotenv(".env")

# Configuration des clés API
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialisation de FastAPI
app = FastAPI(
    title="KOFFI Agent API",
    description="API pour l'agent KOFFI avec LangGraph",
    version="0.1",
)


# Modèles Pydantic
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False


class ChatResponse(BaseModel):
    message: Message
    metadata: Dict[str, Any]


# Fonction de recherche web améliorée
@tool
def search_web(query: str) -> str:
    """Search the web for current information and return formatted results.
    Use this tool for ANY question about recent events, product releases, specifications,
    news, or information that might have changed after 2023."""
    try:
        tavily_search = TavilySearchResults(
            api_key=TAVILY_API_KEY,
            max_results=5,
            search_depth="advanced",
            max_tokens=2000,
        )
        results = tavily_search.invoke(query)
        # Formatage des résultats
        if not results:
            return f"Aucun résultat trouvé pour la recherche: {query}"
        formatted = [f"Résultats de recherche pour '{query}':\n"]
        for i, result in enumerate(results, 1):
            formatted.append(
                f"\n{i}. {result.get('title', 'Sans titre')}\n"
                f"   {result.get('content', 'Pas de description')}\n"
                f"   Source: {result.get('url', 'N/A')}"
            )
        return "\n".join(formatted)
    except Exception as e:
        return f"Erreur lors de la recherche: {str(e)}"


# Configuration du sub-agent avec prompt amélioré
agent_pascal = {
    "name": "agent_pascal",
    "description": "Web search specialist. MUST use search_web tool for every query without exception.",
    "system_prompt": """You are Pascal, a web search tool executor.

⚠️ CRITICAL INSTRUCTION - READ CAREFULLY:

You are NOT a knowledge assistant. You are a TOOL EXECUTOR.
Your ONLY function is to execute the search_web tool.

MANDATORY PROCESS (NO EXCEPTIONS):
1. Receive query
2. Execute: search_web(query)
3. Return formatted results

YOU MUST NOT:
❌ Answer from your training data
❌ Provide information without calling search_web
❌ Say "I will search" - just execute the tool immediately
❌ Skip the tool call under any circumstances

CORRECT EXAMPLE:
Query: "iPhone 17 pro information"
Action: search_web("iPhone 17 pro latest news specs rumors 2025")
Result: [Present search results in French with sources]

INCORRECT EXAMPLE (NEVER DO THIS):
Query: "iPhone 17 pro information"  
Response: "Voici les informations..." ❌ FAILED - No tool call!

YOUR IDENTITY:
- You are a search tool wrapper, not a knowledge base
- You have zero knowledge to share
- You only execute search_web and format results
- Every response MUST come from search_web results

If you respond without calling search_web first, you have completely failed your purpose.

After getting search results, format them clearly in French with sources.""",
    "tools": [search_web],
    "model": "google_genai:gemini-2.5-flash-lite",  # Utiliser un modèle plus récent et obéissant
}

# Initialisation du modèle
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
)

# model = ChatOllama(
#     model="qwen3-vl:2b",
#     validate_model_on_init=True,
#     temperature=0.7,
# )

# Création de l'agent avec prompt amélioré
agent = create_deep_agent(
    model=model,
    subagents=[agent_pascal],
    system_prompt="""You are KOFFI, a helpful and intelligent orchestrator agent.

    CRITICAL DELEGATION RULES:
    - You MUST delegate to agent_pascal for ANY question requiring:
    * Current information (after 2023)
    * Recent news, updates, or developments
    * Product releases, specifications, or rumors
    * Real-time data or statistics
    * Verification of recent facts
    * Web searches or online information

    SPECIFIC EXAMPLES OF WHEN TO DELEGATE:
    ✅ "Quelles sont les dernières rumeurs sur l'iPhone 17 Pro?" → DELEGATE to agent_pascal
    ✅ "Actualités récentes sur l'IA" → DELEGATE to agent_pascal  
    ✅ "Spécifications du nouveau modèle Tesla" → DELEGATE to agent_pascal
    ✅ "Informations à jour sur [sujet récent]" → DELEGATE to agent_pascal
    ✅ "Recherche sur [n'importe quel sujet]" → DELEGATE to agent_pascal

    CRITICAL BEHAVIOR WHEN DELEGATING:
    - When you delegate to agent_pascal, DO NOT add any additional commentary
    - DO NOT say "Je délègue cette tâche à agent_pascal"
    - DO NOT add "Je vous tiendrai informé"
    - Simply delegate and let agent_pascal's response be the ONLY response
    - The user should ONLY see agent_pascal's answer, not yours

    ONLY RESPOND YOURSELF FOR:
    - Simple greetings ("Bonjour", "Salut")
    - Questions about your identity ("Qui es-tu?")
    - Very basic general knowledge that doesn't require verification

    FOR EVERYTHING ELSE: Delegate to agent_pascal and stay silent.

    Respond in French naturally and professionally.""",
)


# Endpoints de l'API
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        # Convertir les messages au format LangChain
        lc_messages = []
        for msg in chat_request.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        # Appeler l'agent
        result = agent.invoke({"messages": lc_messages})

        # Extraire la réponse - chercher le dernier message AIMessage
        ai_response = None
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                ai_response = message
                break

        if not ai_response:
            raise ValueError("Aucune réponse de l'assistant trouvée")

        # Extraire et nettoyer le contenu
        content = extract_content(ai_response)

        # Nettoyage supplémentaire
        if isinstance(content, str):
            # Supprimer les lignes vides multiples
            lines = [line.strip() for line in content.split("\n")]
            content = "\n".join(line for line in lines if line)

        return ChatResponse(
            message=Message(role="assistant", content=content.strip()),
            metadata={
                "model": "gemini-2.5-flash",
                "tokens_used": len(content.split()),
                "message_count": len(result["messages"]),
            },
        )

    except Exception as e:
        import traceback

        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Erreur: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "gemini-2.5-flash",
        "subagents": ["agent_pascal"],
    }


# Test endpoint pour debug
@app.post("/chat/debug")
async def chat_debug(chat_request: ChatRequest):
    """Endpoint de debug pour voir la structure complète de la réponse"""
    try:
        lc_messages = []
        for msg in chat_request.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        result = agent.invoke({"messages": lc_messages})

        # Retourner toute la structure pour debug
        return {
            "message_count": len(result["messages"]),
            "messages": [
                {
                    "type": type(msg).__name__,
                    "content": (
                        str(msg.content)[:200] + "..."
                        if len(str(msg.content)) > 200
                        else str(msg.content)
                    ),
                }
                for msg in result["messages"]
            ],
            "full_result": str(result)[:500],
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent_with_langgraph:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
