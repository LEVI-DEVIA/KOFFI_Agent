"""
Configuration centralisée pour KOFFI Agent
"""

import os

# Charger les variables d'environnement depuis le fichier .env
# Chercher le .env dans le dossier koffi
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    from dotenv import load_dotenv

    load_dotenv(env_path)
    print(f"✅ Variables d'environnement chargées depuis: {env_path}")
else:
    print(f"⚠️ Fichier .env non trouvé: {env_path}")

# API Keys
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DEEPSEEK_API = os.environ.get("DEEPSEEK_API", "")
BYTEZ_API_KEY = os.environ.get("BYTEZ_API_KEY", "")
ZML_API_KEY = os.environ.get("ZML_API_KEY", "")
# Database
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(DATA_DIR, "koffi_memory.db"))

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Agent
# Options de modèles (du plus rapide au plus puissant):
# - gemini-1.5-flash (quota élevé, rapide)
# - gemini-1.5-pro (quota moyen, plus intelligent)
# - gemini-2.5-flash (quota faible, expérimental)
MODEL_NAME = os.getenv(
    "MODEL_NAME", "gemini-2.5-flash"
)  # Modèle par défaut pour éviter les problèmes de quota
TEMPERATURE = 0.5  # Réduit pour des réponses plus rapides et directes

# Session
SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT_SECONDS", 7200))

# Streaming - Optimisé pour réactivité
STREAMING_WORD_DELAY = (
    0.01  # Délai entre les mots en streaming (10ms pour plus de réactivité)
)
