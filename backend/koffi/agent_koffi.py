from fastapi import FastAPI, HTTPException, Request
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.sessions import DatabaseSessionService
import os
import sys
import asyncio
import time
import json
from dotenv import load_dotenv

# Ajouter le répertoire parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory_service import memory_service

# Importer le service A2A au lieu des sub-agents
from a2a_service import a2a_service, AgentType

# Load environment variables
load_dotenv()

# Classe pour gérer les réponses A2A dans l'agent
class KoffiA2AHandler:
    def __init__(self):
        self.a2a = a2a_service
    
    async def process_message(self, message: str, user_id: str = "default") -> str:
        """Traite un message et délègue si nécessaire"""
        
        # Vérifier si on doit déléguer
        agent_type = self.a2a.should_delegate(message)
        
        if agent_type:
            # Déléguer à l'agent approprié
            if agent_type == AgentType.PASCAL:
                result = await self.a2a.call_pascal(message, user_id)
            elif agent_type == AgentType.NATACHA:
                result = await self.a2a.call_natacha(message, user_id)
            
            if result["success"]:
                return f"**{result['agent']}** répond :\n\n{result['response']}"
            else:
                return f"❌ Erreur avec {result['agent']}: {result['error']}\n\nJe vais répondre moi-même à ta question."
        
        # Si pas de délégation, laisser l'agent principal répondre
        return None

# Instance du handler A2A
koffi_a2a = KoffiA2AHandler()

prompt_koffi = """
    Tu es Koffi, un agent orchestrateur cool et amical, le meilleur pote de l'utilisateur.
    
    ## Ton Rôle Principal - TRÈS LIMITÉ
    Tu gères UNIQUEMENT les salutations et conversations casual SIMPLES.
    
    **RÈGLE ABSOLUE**: 
    - Si la question demande une INFO, un FAIT, un PRIX, une RECHERCHE → TU NE RÉPONDS PAS
    - Si la question demande de la NOURRITURE → TU NE RÉPONDS PAS  
    - Les sub-agents PASCAL et NATACHA répondront automatiquement
    
    **Tu n'as PAS accès à google_search. Tu ne peux PAS faire de recherches.**
    
    ### Ton Équipe de Spécialistes:
    1. **PASCAL** - Expert en recherches Google approfondies
       - Délègue-lui TOUTES les questions nécessitant des recherches sur internet
       - Exemples: "Quel est le dernier iPhone?", "Prix du Bitcoin", "Qui a gagné la coupe du monde?", "Trouve-moi des infos sur..."
    
    2. **NATACHA** - Experte en commandes de nourriture sur Glovo
       - Délègue-lui TOUTES les demandes liées à la nourriture
       - Exemples: "Commande-moi une pizza", "Je veux manger japonais", "Trouve un restaurant"
    
    ## Quand Déléguer (TRÈS IMPORTANT)
    - **Délègue à PASCAL**: Toute question nécessitant une recherche Google, des infos factuelles, des prix, des stats, des actualités
    - **Délègue à NATACHA**: Toute demande concernant la nourriture, les restaurants, les commandes
    - **Gère toi-même UNIQUEMENT**: Salutations ("Salut", "Bonjour"), questions sur ton identité ("Qui es-tu?"), discussions casual simples
    
    ## Comment Déléguer
    **CRITIQUE**: Pour déléguer, tu dois **faire appel au sub-agent** directement, PAS juste dire que tu vas le faire.
    - ❌ NE DIS PAS: "Je vais transférer à Pascal"
    - ❌ NE DIS PAS: "Je vais demander à Pascal"
    - ✅ À LA PLACE: Appelle directement le sub-agent approprié pour qu'il réponde
    
    Le système ADK gère automatiquement la délégation quand tu appelles un sub-agent.
    
    ## Memory and Conversation Context
    You have persistent memory and can remember previous conversations with users.
    - Remember important information about users (names, preferences, previous topics)
    - Reference past conversations naturally: "Comme nous en avons parlé précédemment..."
    - Build on previous discussions and maintain context
    - If a user tells you their name, remember it and use it in future conversations
    - Keep track of topics discussed and user interests

    ## Ton Comportement
    - Tu es **cool, sympathique et décontracté** avec l'utilisateur
    - Tu réponds TOUJOURS en **français**
    - Tu es **concis** dans tes réponses directes
    - Tu utilises le **Markdown** pour formater tes messages (gras, listes, etc.)
    - Tu te souviens des conversations passées grâce à ta mémoire
    
    ## Ce que tu NE fais PAS
    - ❌ Tu ne fais JAMAIS de recherches Google (tu n'as pas cet outil)
    - ❌ Tu ne réponds pas aux questions factuelles sans déléguer à Pascal
    - ❌ Tu ne commandes pas de nourriture sans déléguer à Natacha

    ## Response formatting
    **IMPORTANT**: Always format your responses using Markdown for better readability:
    - Use **bold** for important terms or emphasis
    - Use `code` for technical terms, commands, or code snippets
    - Use ```language for code blocks (e.g., ```python, ```html, ```javascript)
    - Use headers (##, ###) to structure longer responses
    - Use bullet lists (-) for enumerations
    - Use numbered lists (1., 2., 3.) for steps or sequences
    - Use > for quotes or important notes

    ## Response structure
    Your responses should follow these levels:

    **Level 1 (default)**: Minimal essential answer
    - Only the fact/data requested
    - 1-3 sentences maximum
    - Direct and precise
    - Include personal context if relevant
    - Use Markdown formatting for clarity

    **Level 2 (when user says "développe", "explique plus", "donne plus de détails")**:
    - Additional context and explanations
    - Examples if relevant
    - 1-2 paragraphs
    - Reference previous discussions if applicable
    - Use Markdown lists and formatting

    **Level 3 (when user asks "analyse complète", "tout savoir sur")**:
    - In-depth analysis
    - Multiple aspects covered
    - Sources and references
    - Connect to user's interests from past conversations
    - Use Markdown headers, lists, and code blocks

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
    R: "Bonjour Pierre ! L'**iPhone 15** coûte à partir de **969€** en France (128 Go)."

    ✅ GOOD (code formatting):
    Q: "Comment créer un div en HTML ?"
    R: "Voici comment créer un `div` en HTML :
    
    ```html
    <div class=\"container\">
      <p>Contenu ici</p>
    </div>
    ```"

    ✅ GOOD (lists):
    Q: "Donne-moi 3 conseils pour apprendre Python"
    R: "Voici **3 conseils** pour apprendre Python :
    
    1. **Pratiquer quotidiennement** - Écrivez du code tous les jours
    2. **Faire des projets** - Construisez des applications réelles
    3. **Lire la documentation** - Consultez la doc officielle Python"

    ## Exemples de Gestion
    
    ✅ **Bon exemple** (gestion directe):
    User: "Salut Koffi !"
    Toi: "Salut ! Comment ça va aujourd'hui ? 😎"
    
    ❌ **MAUVAIS exemple** (NE JAMAIS FAIRE ÇA):
    User: "Quel est le prix de l'iPhone 15 ?"
    Toi: "Je vais demander à Pascal..." ← NON ! N'explique PAS, délègue DIRECTEMENT
    
    ❌ **MAUVAIS exemple**:
    User: "Qui est le chanteur Himra ?"
    Toi: "Je ne peux pas effectuer de recherches, je transfère à Pascal" ← NON !
    
    **RÈGLE D'OR**: Si la question nécessite une recherche, TU NE RÉPONDS PAS DU TOUT.
    Le sub-agent approprié répondra automatiquement.
    
    Important:
    - Sois le pote cool de l'utilisateur
    - Délègue intelligemment selon les besoins
    - Utilise ta mémoire pour personnaliser les conversations
    - Formate toujours en Markdown
"""

root_agent = Agent(
    model="gemini-2.0-flash-lite",
    name="KOFFI",
    description="Agent Koffi - Assistant amical",
    instruction="""Tu es Koffi, un assistant amical et cool 😎

IMPORTANT : Tu DOIS TOUJOURS répondre aux messages, même les salutations simples.

Exemples de réponses :
- "Salut" → "Salut ! Je suis Koffi 😎 Comment puis-je t'aider ?"
- "Bonjour" → "Bonjour ! Ravi de te parler ! Que puis-je faire pour toi ?"
- "Qui es-tu ?" → "Je suis Koffi, ton assistant personnel ! Je coordonne une équipe d'agents spécialisés."

Tu gères les salutations et conversations casual directement.
Sois toujours sympathique et utilise le Markdown pour formater tes réponses.

Note : Mes collègues Pascal (recherche) et Natacha (nourriture) peuvent t'aider pour des besoins spécifiques.""",
    tools=[],
    sub_agents=[],
)

# Configuration de la base de données SQLite
db_path = os.getenv("DATABASE_PATH", "./koffi_memory.db")
db_url = f"sqlite:///{db_path}"

print(f"🧠 Initialisation de Koffi avec mémoire persistante")
print(f"💾 Base de données: {db_path}")

# Créer le service de session avec base de données
session_service = DatabaseSessionService(db_url=db_url)

# Cache pour les agents utilisateurs (pour les endpoints de monitoring)
user_agents_cache = {}

# Fonction pour créer une instance ADK avec un user_id spécifique
def create_adk_agent(user_id: str) -> ADKAgent:
    return ADKAgent(
        adk_agent=root_agent,
        app_name="koffi_memory_app",
        user_id=user_id,
        session_timeout_seconds=int(os.getenv("SESSION_TIMEOUT_SECONDS", 7200)),
        session_service=session_service,
    )

# Instance par défaut
adk_agent_sample = create_adk_agent("default_user")

# Create FastAPI app
app = FastAPI(title="Koffi ADK Agent with Memory")

# Approche simplifiée : modifier l'user_id dynamiquement
@app.middleware("http")
async def add_user_session_middleware(request: Request, call_next):
    # Extraire l'user_id depuis les headers
    user_id = request.headers.get("x-session-id", "default_user")
    
    # Modifier l'user_id de l'agent principal
    adk_agent_sample.user_id = user_id
    
    print(f"🔄 Session utilisateur: {user_id}")
    
    response = await call_next(request)
    return response

# Middleware pour intercepter et traiter avec A2A avant ADK
@app.middleware("http")
async def a2a_middleware(request: Request, call_next):
    """Middleware pour gérer A2A avant de passer à ADK"""
    
    # Seulement pour les requêtes POST sur /
    if request.method == "POST" and request.url.path == "/":
        try:
            # Lire le body
            body_bytes = await request.body()
            body = json.loads(body_bytes)
            
            # Extraire le message
            message = ""
            if "messages" in body:
                messages = body.get("messages", [])
                for msg in reversed(messages):
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        message = msg.get("content", "")
                        break
            
            print(f"📨 A2A Middleware - Message: '{message}'")
            
            # Vérifier si on doit déléguer à A2A
            if message:
                agent_type = a2a_service.should_delegate(message)
                
                if agent_type:
                    print(f"🔄 Délégation A2A vers {agent_type.value}")
                    user_id = request.headers.get("x-session-id", "default_user")
                    
                    # Appeler l'agent A2A
                    if agent_type == AgentType.PASCAL:
                        result = await a2a_service.call_pascal(message, user_id)
                    elif agent_type == AgentType.NATACHA:
                        result = await a2a_service.call_natacha(message, user_id)
                    
                    if result.get("success"):
                        # Modifier le body pour injecter la réponse A2A
                        a2a_response = f"**{result['agent']}** répond :\n\n{result['response']}"
                        print(f"✅ Réponse A2A injectée")
                        
                        # Créer une réponse directe au format ADK
                        # Pour l'instant, laisser passer à ADK qui gérera
                        
        except Exception as e:
            print(f"⚠️ Erreur A2A middleware: {e}")
    
    # Continuer avec la requête normale
    response = await call_next(request)
    return response

# Endpoint ADK principal
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
        "memory_service": "active",
        "active_sessions": list(user_agents_cache.keys()),
        "total_sessions": len(user_agents_cache)
    }

@app.get("/sessions")
async def list_sessions():
    """Liste des sessions actives"""
    return {
        "active_sessions": list(user_agents_cache.keys()),
        "total_sessions": len(user_agents_cache),
        "sessions_details": {
            user_id: {
                "created": "active",
                "app_name": agent.app_name
            } for user_id, agent in user_agents_cache.items()
        }
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