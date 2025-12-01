# KOFFI Agent Backend

Backend modulaire pour l'agent KOFFI avec LangGraph et mémoire persistante.

## 🏗️ Structure du Projet

```
backend/
├── agents/              # Agents (KOFFI principal + sous-agents)
│   ├── koffi_agent.py  # Agent orchestrateur principal
│   └── agent_pascal.py # Agent de recherche web
├── api/                 # Routes et modèles FastAPI
│   ├── routes.py       # Endpoints de l'API
│   └── models.py       # Modèles Pydantic
├── config/             # Configuration
│   └── settings.py     # Variables d'environnement et config
├── services/           # Services métier
│   ├── memory_service.py   # Gestion de la mémoire persistante
│   └── search_service.py   # Service de recherche web (Tavily)
├── utils/              # Utilitaires
│   └── helpers.py      # Fonctions helper
├── data/               # Base de données SQLite
│   └── koffi_memory.db
├── main.py             # Point d'entrée principal
├── requirements.txt    # Dépendances Python
├── run.sh             # Script de démarrage
└── .env               # Variables d'environnement
```

## 🚀 Démarrage Rapide

### Option 1: Script automatique (recommandé)
```bash
./run.sh
```

### Option 2: Manuel
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

## 🔧 Configuration

Créer un fichier `.env` avec:
```env
GEMINI_API_KEY=votre_clé_api
TAVILY_API_KEY=votre_clé_tavily
HOST=0.0.0.0
PORT=8000
```

## 📡 API Endpoints

- `POST /chat` - Chat avec l'agent (streaming ou normal)
- `GET /health` - Vérification de santé
- `POST /memory-test` - Test de la mémoire
- `POST /add-fact` - Ajouter un fait important
- `POST /clear-memory` - Effacer la mémoire
- `GET /memory-status` - Statut de la mémoire

## 🧠 Fonctionnalités

- ✅ Agent orchestrateur avec délégation intelligente
- ✅ Sous-agent de recherche web (agent_pascal)
- ✅ Mémoire persistante avec SQLite
- ✅ Streaming de réponses mot par mot
- ✅ Gestion de sessions utilisateur
- ✅ Architecture modulaire et maintenable
