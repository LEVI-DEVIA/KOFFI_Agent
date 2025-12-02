# 🚀 Guide de Démarrage Rapide - KOFFI Agent

## 📋 Prérequis

- Python 3.12+
- Node.js 18+
- npm ou yarn
- Clés API : Gemini, Tavily

## 🔧 Installation

### 1. Backend (Python)

```bash
cd backend

# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

### 2. Frontend (Next.js)

```bash
cd frontend

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env.local
# Éditer .env.local si nécessaire
```

## 🚀 Lancement

### Option 1 : Script Automatique (Recommandé)

```bash
# Terminal 1 - Backend
cd backend
./run.sh

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Option 2 : Manuel

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🌐 Accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🎤 Fonctionnalités Audio

### Reconnaissance Vocale (STT)
1. Clique sur le bouton microphone 🎤
2. Parle en français
3. Clique à nouveau pour arrêter
4. Ta question est transcrite automatiquement

### Synthèse Vocale (TTS)
- **Question vocale** → Koffi répond en audio 🔊
- **Question texte** → Koffi répond en texte 📝
- Bouton "Arrêter" pour stopper la lecture

## 🧪 Test Rapide

### Test Backend
```bash
curl http://localhost:8000/health
```

### Test Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "x-session-id: test_user" \
  -d '{
    "messages": [
      {"role": "user", "content": "Bonjour"}
    ],
    "stream": false
  }'
```

## 📁 Structure du Projet

```
KOFFI_Agent/
├── backend/              # API Python FastAPI
│   ├── agents/          # Agents IA (Koffi + Pascal)
│   ├── api/             # Routes et modèles
│   ├── config/          # Configuration
│   ├── services/        # Services (mémoire, recherche)
│   ├── utils/           # Utilitaires
│   ├── data/            # Base de données SQLite
│   └── main.py          # Point d'entrée
│
└── frontend/            # Interface Next.js
    ├── app/             # Pages et routes
    ├── hooks/           # Hooks React (audio, voice)
    └── public/          # Assets statiques
```

## 🔑 Variables d'Environnement

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

## 🐛 Dépannage

### Backend ne démarre pas
- Vérifier que le venv est activé
- Vérifier les clés API dans .env
- Vérifier que le port 8000 est libre

### Frontend ne se connecte pas
- Vérifier que le backend est démarré
- Vérifier l'URL dans .env.local
- Vérifier la console du navigateur

### Audio ne fonctionne pas
- Vérifier les permissions du microphone
- Utiliser Chrome ou Edge
- Vérifier que le son n'est pas coupé

## 📚 Documentation

- [Backend README](backend/README.md)
- [Structure Backend](backend/STRUCTURE_FINALE.md)
- [Commandes Backend](backend/COMMANDES.md)
- [Fonctionnalités Audio](frontend/AUDIO_FEATURES.md)

## 🎯 Exemples d'Utilisation

### Conversation Vocale
```
🎤 "Bonjour Koffi, comment vas-tu ?"
🔊 Koffi répond en audio

🎤 "Quelles sont les dernières news sur l'IA ?"
🔊 Koffi recherche sur le web et répond en audio
```

### Conversation Texte
```
⌨️ "Explique-moi la théorie de la relativité"
📝 Koffi répond en texte avec formatage Markdown
```

### Conversation Mixte
```
⌨️ "Bonjour"
📝 Réponse texte

🎤 "Recherche des infos sur Tesla"
🔊 Réponse audio avec recherche web
```

## 🚀 Prochaines Étapes

1. Tester les fonctionnalités de base
2. Essayer la reconnaissance vocale
3. Tester la recherche web avec agent_pascal
4. Explorer la mémoire persistante
5. Personnaliser les prompts des agents

## 💡 Conseils

- Utilise Chrome ou Edge pour de meilleurs résultats audio
- La mémoire est persistante entre les sessions
- Tu peux créer une nouvelle discussion pour réinitialiser la mémoire
- Les recherches web sont automatiques pour les questions récentes

## 🆘 Support

En cas de problème :
1. Vérifier les logs du backend
2. Vérifier la console du navigateur
3. Consulter la documentation
4. Vérifier les issues GitHub
