# KOFFI Agent 🤖

Agent intelligent spécialisé dans la recherche internet qui délivre des informations précises et à jour, toujours en français.

## 📋 Description

KOFFI est un agent conversationnel basé sur Google ADK (Agent Development Kit) et Gemini 2.0, avec une interface utilisateur moderne construite avec Next.js et CopilotKit. L'agent est capable de :

- 🔍 Effectuer des recherches internet en temps réel
- 💬 Répondre de manière concise et précise
- 🇫🇷 Communiquer exclusivement en français
- 🎯 Adapter le niveau de détail selon les besoins

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
- **Agent** : Google ADK avec Gemini 2.0 Flash
- **Outils** : Google Search
- **Port** : 8000

### Frontend
- **Framework** : Next.js 16 (App Router)
- **UI** : CopilotKit + Tailwind CSS
- **Port** : 3000

## 🚀 Installation

### Prérequis

- Python 3.10+
- Node.js 18+
- npm ou yarn
- Compte Google Cloud avec API activées

### 1. Configuration du Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

### 2. Configuration du Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Le frontend se connecte automatiquement au backend sur localhost:8000
```

## 🎮 Utilisation

### Démarrer le Backend

```bash
cd backend
make run
# ou
adk web
```

Le serveur démarre sur `http://localhost:8000`

### Démarrer le Frontend

```bash
cd frontend
npm run dev
```

L'interface est accessible sur `http://localhost:3000`

## 📝 Configuration

### Variables d'environnement (Backend)

Créez un fichier `.env` dans le dossier `backend/` :

```env
GOOGLE_API_KEY=votre_clé_api_google
# Ajoutez d'autres variables selon vos besoins
```

## 🧪 Tests

```bash
cd backend
pytest tests/
```

## 📚 Documentation

- [Documentation Backend](./backend/README.md)
- [Documentation Frontend](./frontend/README.md)
- [Notebooks de développement](./docs/)

## 🛠️ Développement

### Structure du code

- `backend/koffi/agent.py` : Configuration de l'agent KOFFI
- `frontend/app/` : Pages et composants Next.js
- `frontend/app/api/copilotkit/` : Route API pour la connexion agent

### Commandes utiles (Backend)

```bash
make install-packages  # Installer les dépendances
make run              # Lancer le serveur
make save             # Sauvegarder les dépendances
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Voir le fichier [LICENSE](./backend/LICENSE)

## 👤 Auteur

Levi - KOFFI Agent Project

---

**Note** : Ce projet utilise Google ADK et nécessite des clés API Google Cloud valides pour fonctionner.
