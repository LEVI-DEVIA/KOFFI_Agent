"""
KOFFI Agent - Point d'entrée principal
"""

import os
import sys
from pathlib import Path

# Ajouter le dossier backend au path pour les imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

# Imports des modules
from config.settings import HOST, PORT, DATA_DIR, DATABASE_PATH
from api import routes
from agents.koffi_agent import create_koffi_agent

# Créer le dossier data s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Variable globale pour le checkpointer
memory_checkpointer = None
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global memory_checkpointer, agent

    print("🚀 Démarrage de KOFFI Agent API...")
    print(f"💾 Base de données: {DATABASE_PATH}")

    # Initialiser le checkpointer asynchrone
    db_path_full = os.path.join(DATA_DIR, os.path.basename(DATABASE_PATH))

    # Créer la connexion qui restera ouverte pendant toute la durée de vie de l'app
    conn = await aiosqlite.connect(db_path_full)
    memory_checkpointer = AsyncSqliteSaver(conn)
    await memory_checkpointer.setup()
    print("✅ Checkpointer AsyncSqliteSaver initialisé")

    # Créer l'agent
    agent = create_koffi_agent(memory_checkpointer)
    print("✅ Agent KOFFI créé")

    # Passer l'agent aux routes
    routes.set_agent(agent)

    yield

    # Fermer la connexion à l'arrêt
    print("👋 Arrêt de KOFFI Agent API...")
    await conn.close()
    print("✅ Connexion à la base de données fermée")


# Créer l'application FastAPI
app = FastAPI(
    title="KOFFI Agent API",
    description="API pour l'agent KOFFI avec LangGraph et mémoire persistante",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurer les routes
routes.setup_routes(app)


if __name__ == "__main__":
    import uvicorn

    print(f"\n🚀 Démarrage de Koffi")
    print(f"🌐 Serveur: http://{HOST}:{PORT}")
    print(f"📚 Documentation: http://{HOST}:{PORT}/docs")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
