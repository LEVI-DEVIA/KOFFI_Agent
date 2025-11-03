from fastapi import FastAPI, HTTPException
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.sessions import DatabaseSessionService
import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory_service import memory_service

# Load environment variables
load_dotenv()

prompt_koffi = """
    You are Koffi, a helpful agent specialized in internet research that delivers precise, up-to-date information.
    
    ## Memory and Conversation Context
    You have persistent memory and can remember previous conversations with users.
    - Remember important information about users (names, preferences, previous topics)
    - Reference past conversations naturally: "Comme nous en avons parlé précédemment..."
    - Build on previous discussions and maintain context
    - If a user tells you their name, remember it and use it in future conversations
    - Keep track of topics discussed and user interests

    ## Internet Research Operations
    You can perform internet searches using:
    - `google_search`: Search the internet for current, accurate information on any topic

    ## Language
    - You MUST ALWAYS respond in French, regardless of the language used in the question
    - All your responses must be exclusively in French

    ## Be precise and concise
    Be direct when handling search requests. Don't provide unnecessary information unless explicitly asked.

    For example:
    - When the user asks a simple question, give a simple answer (1-3 sentences maximum)
    - If the user asks "What is X?", just define X briefly
    - Only expand if the user explicitly asks for more details with phrases like "développe", "explique plus", "donne plus de détails"

    ## Search guidelines
    For internet searches:
    - ALWAYS use google_search for factual information, current prices, recent events, statistics, or any data that needs to be up-to-date
    - Never rely solely on your internal knowledge for factual queries
    - Use google_search to verify information before responding

    ## Response structure
    Your responses should follow these levels:

    **Level 1 (default)**: Minimal essential answer
    - Only the fact/data requested
    - 1-3 sentences maximum
    - Direct and precise
    - Include personal context if relevant

    **Level 2 (when user says "développe", "explique plus", "donne plus de détails")**:
    - Additional context and explanations
    - Examples if relevant
    - 1-2 paragraphs
    - Reference previous discussions if applicable

    **Level 3 (when user asks "analyse complète", "tout savoir sur")**:
    - In-depth analysis
    - Multiple aspects covered
    - Sources and references
    - Connect to user's interests from past conversations

    ## Examples

    ❌ BAD (too much information):
    Q: "Quelle est la capitale de la France ?"
    R: "La capitale de la France est Paris. Paris est également la ville la plus peuplée de France avec plus de 2 millions d'habitants intra-muros et 12 millions dans l'agglomération. Fondée au IIIe siècle avant J.-C., Paris est un centre culturel, économique et politique majeur..."

    ✅ GOOD (precise):
    Q: "Quelle est la capitale de la France ?"
    R: "Paris."

    ✅ GOOD (with memory):
    User: "Je m'appelle Pierre"
    R: "Enchanté Pierre ! Comment puis-je vous aider aujourd'hui ?"
    
    Later conversation:
    Q: "Quel est le prix de l'iPhone 15 ?"
    R: "Bonjour Pierre ! L'iPhone 15 coûte à partir de 969€ en France (128 Go)."

    Important:
    - Be super concise in your responses and only return the information requested (not extra information)
    - ALWAYS use google_search for factual, current, or verifiable information
    - ALWAYS respond in French
    - NEVER show the raw response from tool outputs. Instead, use the information to answer the question naturally
    - Only expand your answer when the user explicitly requests more details
    - Use your memory to provide personalized responses and maintain conversation continuity
"""

root_agent = Agent(
    model="gemini-2.5-flash-lite-preview-09-2025",
    name="KOFFI",
    description="Agent Koffi best friend",
    instruction=prompt_koffi,
    tools=[google_search],
    # sub_agents=[natacha_agent, pascal_agent],
)

# Configuration de la base de données SQLite
db_path = os.getenv("DATABASE_PATH", "./koffi_memory.db")
db_url = f"sqlite:///{db_path}"

print(f"🧠 Initialisation de Koffi avec mémoire persistante")
print(f"💾 Base de données: {db_path}")

# Créer le service de session avec base de données
session_service = DatabaseSessionService(db_url=db_url)

# Create ADK middleware agent instance avec mémoire persistante
adk_agent_sample = ADKAgent(
    adk_agent=root_agent,
    app_name="koffi_memory_app",
    user_id="default_user",
    session_timeout_seconds=int(os.getenv("SESSION_TIMEOUT_SECONDS", 7200)),
    session_service=session_service,  # Utiliser le service de base de données
)

# Create FastAPI app
app = FastAPI(title="Koffi ADK Agent with Memory")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_agent_sample, path="/")

# Endpoints supplémentaires pour la gestion de la mémoire
@app.post("/memory-test")
async def test_memory():
    """Test des fonctionnalités de mémoire"""
    try:
        session_id = memory_service.get_or_create_session("koffi_memory_app", "test_user")
        context = memory_service.get_memory_context(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "memory_context": context,
            "message": "Memory service is working"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-fact")
async def add_important_fact(fact: str, user_id: str = "default_user"):
    """Ajouter un fait important à la mémoire"""
    try:
        session_id = memory_service.get_or_create_session("koffi_memory_app", user_id)
        memory_service.add_important_fact(session_id, fact)
        
        return {
            "status": "success",
            "message": f"Fait ajouté: {fact}",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-memory")
async def clear_memory(user_id: str = "default_user"):
    """Effacer la mémoire d'un utilisateur"""
    try:
        session_id = memory_service.get_or_create_session("koffi_memory_app", user_id)
        memory_service.clear_memory(session_id)
        
        return {
            "status": "success",
            "message": "Mémoire effacée",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory-status")
async def memory_status():
    """Statut du système de mémoire"""
    return {
        "status": "active",
        "database_path": db_path,
        "database_url": db_url,
        "session_timeout": os.getenv("SESSION_TIMEOUT_SECONDS", 7200),
        "memory_service": "active"
    }

# Démarrage du serveur
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🚀 Démarrage de Koffi avec mémoire")
    print(f"🌐 Serveur: http://{host}:{port}")
    print(f"📚 Endpoints disponibles:")
    print(f"  - POST / : Endpoint principal ADK")
    print(f"  - POST /memory-test : Test de la mémoire")
    print(f"  - POST /add-fact : Ajouter un fait important")
    print(f"  - POST /clear-memory : Effacer la mémoire")
    print(f"  - GET /memory-status : Statut de la mémoire")
    print(f"\n💡 La base de données SQLite sera créée automatiquement au premier usage")
    
    uvicorn.run(app, host=host, port=port)
