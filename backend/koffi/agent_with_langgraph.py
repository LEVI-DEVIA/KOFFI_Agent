import os
import sys
import json
import asyncio
import aiosqlite
from typing import List, Literal, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver # <--- CHANGEMENT ICI
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from contextlib import asynccontextmanager # <--- AJOUT ICI

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory_service import memory_service

def extract_content(message):
    """Extrait le contenu texte d'un message LangChain de manière robuste."""
    if hasattr(message, "content"):
        content = message.content
    else:
        content = message

    if isinstance(content, str):
        return content
    elif isinstance(content, list):
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

# Configuration de la base de données pour la mémoire
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)
db_path = os.getenv("DATABASE_PATH", os.path.join(data_dir, "koffi_langgraph_memory.db"))
print(f"🧠 Initialisation de Koffi LangGraph avec mémoire persistante")
print(f"💾 Base de données: {db_path}")

# Variable globale pour le checkpointer
memory_checkpointer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au démarrage de l'application
    global memory_checkpointer
    print("🚀 Démarrage de KOFFI Agent API...")
    
    # Initialisation du checkpointer asynchrone
    memory_checkpointer = AsyncSqliteSaver.from_conn_string(db_path)
    print("✅ Checkpointer AsyncSqliteSaver initialisé")
    
    yield
    
    # Code exécuté à l'arrêt de l'application
    print("🛑 Arrêt de KOFFI Agent API...")
    if memory_checkpointer:
        await memory_checkpointer.aclose()
        print("✅ Checkpointer fermé")

# Initialisation de FastAPI avec le gestionnaire de cycle de vie
app = FastAPI(
    title="KOFFI Agent API",
    description="API pour l'agent KOFFI avec LangGraph et mémoire persistante",
    version="0.1",
    lifespan=lifespan,
)

# Modèles Pydantic
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

# Fonction de recherche web
@tool
def search_web(query: str) -> str:
    """Search the web for current information and return formatted results."""
    try:
        tavily_search = TavilySearchResults(
            api_key=TAVILY_API_KEY,
            max_results=5,
            search_depth="advanced",
            max_tokens=2000,
        )
        results = tavily_search.invoke(query)
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

# Configuration du sub-agent
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
    "model": "google_genai:gemini-2.5-flash-lite",
}

# Initialisation du modèle
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
)

# Création de l'agent avec prompt amélioré et mémoire asynchrone
agent = create_deep_agent(
    model=model,
    subagents=[agent_pascal],
    checkpointer=memory_checkpointer, # Utiliser le checkpointer asynchrone
    system_prompt="""You are KOFFI, a helpful and intelligent orchestrator agent with persistent memory.
    MEMORY AND CONVERSATION CONTEXT:
    - You have persistent memory and remember previous conversations with users
    - Remember important information about users (names, preferences, previous topics)
    - Reference past conversations naturally: "Comme nous en avons parlé précédemment..."
    - Build on previous discussions and maintain context
    - If a user tells you their name, remember it and use it in future conversations
    - Keep track of topics discussed and user interests
    You are KOFFI, a helpful and intelligent orchestrator agent.
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

# Middleware pour gérer les sessions utilisateur
@app.middleware("http")
async def add_user_session_middleware(request: Request, call_next):
    user_id = request.headers.get("x-session-id", "default_user")
    request.state.user_id = user_id
    print(f"🔄 Session utilisateur: {user_id}")
    response = await call_next(request)
    return response

# Endpoint de chat avec streaming
@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest, request: Request):
    try:
        print(f"📨 Requête reçue: {len(chat_request.messages) if chat_request.messages else 0} messages")
        
        user_id = getattr(request.state, "user_id", "default_user")
        session_id = memory_service.get_or_create_session("koffi_langgraph_app", user_id)
        print(f"💾 Session: {session_id}")
        
        memory_context = memory_service.get_memory_context(session_id)
        
        if not chat_request.messages or len(chat_request.messages) == 0:
            raise HTTPException(status_code=400, detail="Messages array is required and cannot be empty")
        
        lc_messages = []
        if memory_context:
            lc_messages.append(SystemMessage(content=f"Contexte de mémoire:\n{memory_context}"))
        
        for msg in chat_request.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        config = {
            "configurable": {
                "thread_id": f"thread_{user_id}",
            }
        }

        if chat_request.stream:
            async def generate_stream():
                try:
                    user_message = None
                    for message in reversed(lc_messages):
                        if isinstance(message, HumanMessage):
                            user_message = message
                            break
                    
                    print(f"🤖 Appel de l'agent (invoke) pour streaming simulé avec {len(lc_messages)} messages...")
                    
                    # Utiliser invoke au lieu de astream car deepagents ne supporte pas bien astream
                    result = await agent.ainvoke({"messages": lc_messages}, config=config)
                    print(f"✅ Réponse reçue: {len(result['messages'])} messages")
                    
                    # Extraire la réponse
                    ai_response = None
                    for message in reversed(result["messages"]):
                        if isinstance(message, AIMessage):
                            ai_response = message
                            break
                    
                    if not ai_response:
                        raise ValueError("Aucune réponse de l'assistant trouvée")
                    
                    # Extraire le contenu
                    full_response = extract_content(ai_response)
                    print(f"📝 Contenu extrait: {len(full_response)} caractères")
                    
                    # Simuler le streaming en envoyant mot par mot
                    words = full_response.split()
                    for i, word in enumerate(words):
                        # Envoyer le mot avec un espace
                        content_to_send = word + (" " if i < len(words) - 1 else "")
                        yield f"data: {json.dumps({'content': content_to_send, 'type': 'content'})}\n\n"
                        await asyncio.sleep(0.03)  # Délai entre les mots
                    
                    # Mettre à jour la mémoire
                    if user_message:
                        user_content = extract_content(user_message)
                        memory_service.update_conversation_memory(session_id, user_content, full_response)
                    
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                    print(f"✅ Streaming terminé: {len(full_response)} caractères envoyés")
                    
                except Exception as e:
                    import traceback
                    error_detail = f"{str(e)}\n{traceback.format_exc()}"
                    print(f"❌ Erreur streaming: {error_detail}")
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            print(f"🤖 Appel de l'agent avec {len(lc_messages)} messages...")
            result = await agent.ainvoke({"messages": lc_messages}, config=config) # <--- CHANGEMENT ICI (ainvoke au lieu de invoke)
            print(f"✅ Réponse reçue de l'agent: {len(result['messages'])} messages")

            ai_response = None
            user_message = None
            
            for message in reversed(result["messages"]):
                if isinstance(message, AIMessage) and ai_response is None:
                    ai_response = message
                if isinstance(message, HumanMessage) and user_message is None:
                    user_message = message
                if ai_response and user_message:
                    break

            if not ai_response:
                raise ValueError("Aucune réponse de l'assistant trouvée")

            content = extract_content(ai_response)
            if isinstance(content, str):
                lines = [line.strip() for line in content.split("\n")]
                content = "\n".join(line for line in lines if line)

            if user_message:
                user_content = extract_content(user_message)
                memory_service.update_conversation_memory(session_id, user_content, content)

            print(f"📤 Envoi de la réponse: {len(content)} caractères")
            
            response = ChatResponse(
                message=Message(role="assistant", content=content.strip()),
                metadata={
                    "model": "gemini-2.0-flash-exp",
                    "tokens_used": len(content.split()),
                    "message_count": len(result["messages"]),
                    "session_id": session_id,
                    "user_id": user_id,
                },
            )
            
            return response

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Erreur: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "gemini-2.0-flash-exp",
        "subagents": ["agent_pascal"],
        "memory": "enabled",
        "database": db_path,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agent_with_langgraph:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )