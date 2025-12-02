# KOFFI Agent 🤖

Agent intelligent avec reconnaissance vocale et synthèse vocale, spécialisé dans la recherche internet et la conversation naturelle en français.

## 📋 Description

KOFFI est un agent conversationnel moderne basé sur LangGraph et Gemini 2.5, avec une interface Next.js élégante. L'agent est capable de :

- 🔍 Effectuer des recherches internet en temps réel (via agent_pascal)
- 🎤 Comprendre les questions vocales (Speech-to-Text)
- 🔊 Répondre en audio (Text-to-Speech)
- 💬 Converser de manière naturelle avec streaming
- 🧠 Mémoriser les conversations (mémoire persistante)
- 🇫🇷 Communiquer exclusivement en français
- 🎯 Déléguer intelligemment aux sous-agents

## 🏗️ Architecture

Le projet est divisé en deux parties principales :

```
KOFFI_Agent/
├── backend/          # API Python avec FastAPI + Google ADK
├── frontend/         # Interface Next.js avec CopilotKit
└── docs/            # Documentation et notebooks
```

### Backend
- **Framework** : FastAPI
- **Agent** : LangGraph + DeepAgents
- **LLM** : Gemini 2.5 Flash
- **Recherche** : Tavily API
- **Mémoire** : SQLite + AsyncSqliteSaver
- **Port** : 8000

### Frontend
- **Framework** : Next.js 16 (App Router)
- **UI** : Tailwind CSS + React Markdown
- **Audio** : Web Speech API (STT + TTS)
- **Port** : 3000

## 🚀 Installation Rapide

Voir le [Guide de Démarrage Complet](GUIDE_DEMARRAGE.md) pour plus de détails.

### Prérequis

- Python 3.12+
- Node.js 18+
- npm ou yarn
- Clés API : Gemini, Tavily

### 1. Backend

```bash
cd backend
./run.sh  # Installation et démarrage automatiques
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🎮 Utilisation

### Accès
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

### Fonctionnalités Audio

#### 🎤 Reconnaissance Vocale
1. Clique sur le bouton microphone
2. Parle en français
3. Clique à nouveau pour arrêter
4. Ta question est transcrite automatiquement

#### 🔊 Synthèse Vocale
- **Question vocale** → Koffi répond en audio
- **Question texte** → Koffi répond en texte
- Bouton "Arrêter" pour stopper la lecture

Voir [Documentation Audio](frontend/AUDIO_FEATURES.md) pour plus de détails.

## 📝 Configuration

### Backend (.env)
```env
GEMINI_API_KEY=votre_clé_gemini
TAVILY_API_KEY=votre_clé_tavily
HOST=0.0.0.0
PORT=8000
MODEL_NAME=gemini-2.5-flash
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Tests

### Backend
```bash
cd backend
python test_structure.py  # Test de la structure
curl http://localhost:8000/health  # Test de santé
```

### Frontend
```bash
cd frontend
npm run build  # Test de compilation
```

## 📚 Documentation

- [Guide de Démarrage](GUIDE_DEMARRAGE.md) - Installation et utilisation
- [Backend README](backend/README.md) - Documentation backend
- [Structure Backend](backend/STRUCTURE_FINALE.md) - Architecture détaillée
- [Commandes Backend](backend/COMMANDES.md) - Commandes utiles
- [Fonctionnalités Audio](frontend/AUDIO_FEATURES.md) - Guide audio complet
- [Changelog Audio](CHANGELOG_AUDIO.md) - Historique des fonctionnalités

## 🛠️ Développement

### Structure Modulaire

```
backend/
├── agents/          # Agents IA (koffi + pascal)
├── api/             # Routes et modèles FastAPI
├── config/          # Configuration centralisée
├── services/        # Services (mémoire, recherche)
├── utils/           # Utilitaires
└── main.py          # Point d'entrée

frontend/
├── app/             # Pages Next.js
├── hooks/           # Hooks React (audio, voice)
└── public/          # Assets statiques
```

### Agents

- **koffi_agent** : Agent orchestrateur principal
- **agent_pascal** : Spécialiste recherche web (Tavily)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Voir le fichier [LICENSE](./backend/LICENSE)

## ✨ Fonctionnalités Principales

- ✅ Chat avec streaming en temps réel
- ✅ Reconnaissance vocale (Speech-to-Text)
- ✅ Synthèse vocale (Text-to-Speech)
- ✅ Mémoire persistante entre sessions
- ✅ Recherche web automatique
- ✅ Délégation intelligente aux sous-agents
- ✅ Interface moderne et responsive
- ✅ Support Markdown avec coloration syntaxique

## 🌐 Compatibilité

### Navigateurs
- ✅ Chrome / Edge (Recommandé)
- ✅ Safari
- ✅ Firefox

### Systèmes
- ✅ Windows 10/11
- ✅ macOS 13+
- ✅ Linux (Ubuntu 22.04+)

## 👤 Auteur

**ASSALE YAO** - AI Engineer

## 📄 Licence

Voir le fichier [LICENSE](backend/LICENSE)

---

**Note** : Ce projet utilise Gemini 2.5 Flash et Tavily API. Des clés API valides sont nécessaires pour fonctionner.
