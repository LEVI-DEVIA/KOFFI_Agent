# 🚀 Guide de Démarrage - KOFFI Agent

## Démarrage Rapide

### Backend

```bash
# 1. Activer l'environnement virtuel
source .KOFFI_Agent/bin/activate

# 2. Installer les dépendances (si nécessaire)
pip install -r backend/requirements.txt

# 3. Lancer le backend
cd backend/koffi
python koffi_agent.py
```

Le serveur démarre sur `http://localhost:8000`

### Frontend

```bash
# Dans un autre terminal

# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer les dépendances (si nécessaire)
npm install

# 3. Lancer le frontend
npm run dev
```

Le frontend démarre sur `http://localhost:3000`

## Vérification

### Backend

```bash
curl http://localhost:8000/health
```

Réponse attendue:

```json
{
  "status": "healthy",
  "model": "gemini-2.5-flash",
  "subagents": ["agent_pascal"],
  "memory": "enabled"
}
```

### Frontend

Ouvrir `http://localhost:3000` dans le navigateur

## Structure du Projet

```
KOFFI_Agent/
├── backend/
│   ├── koffi/
│   │   ├── koffi_agent.py    # ⭐ Fichier principal du backend
│   │   ├── data/              # Bases de données
│   │   └── .env               # Configuration (clés API)
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # ⭐ Page principale
│   │   └── api/chat/          # API routes
│   ├── hooks/                 # Hooks React
│   └── package.json
│
└── .KOFFI_Agent/              # Environnement virtuel Python
```

## Configuration

### Backend (.env)

Créer `backend/koffi/.env`:

```env
TAVILY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here

HOST=0.0.0.0
PORT=8000
DATABASE_PATH=./koffi_memory.db
```

### Frontend (.env.local)

Créer `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:3000
```

## Fonctionnalités

- ✅ Chat avec streaming
- ✅ Mémoire persistante
- ✅ Recherche web (agent Pascal)
- ✅ Reconnaissance vocale (Chrome/Edge/Safari)
- ✅ Sessions utilisateur
- ✅ Interface moderne

## Problèmes Courants

### Backend ne démarre pas

1. Vérifier l'environnement virtuel:

```bash
which python
# Devrait afficher: .../KOFFI_Agent/.KOFFI_Agent/bin/python
```

2. Réinstaller les dépendances:

```bash
pip install -r backend/requirements.txt
```

3. Vérifier les clés API dans `.env`

### Frontend ne démarre pas

1. Réinstaller les dépendances:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

2. Vérifier Node.js:

```bash
node --version  # Devrait être >= 18
```

### Erreur de connexion

1. Vérifier que le backend tourne sur le bon port
2. Vérifier `BACKEND_URL` dans `frontend/.env.local`
3. Désactiver le firewall si nécessaire

## Documentation

- `backend/DEMARRAGE_RAPIDE.md` - Guide backend détaillé
- `backend/koffi/README.md` - Documentation de l'API
- `backend/REORGANISATION_COMPLETE.md` - Architecture

## Support

Pour toute question ou problème:

1. Vérifier les logs du backend
2. Vérifier la console du navigateur (F12)
3. Consulter la documentation

---

**Développé par ASSALE YAO - AI ENGINEER**
