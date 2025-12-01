# Structure Finale du Backend KOFFI

## 📁 Organisation des Fichiers

Le backend a été complètement réorganisé pour une architecture modulaire et maintenable :

```
backend/
├── agents/                    # 🤖 Agents IA
│   ├── __init__.py
│   ├── koffi_agent.py        # Agent orchestrateur principal
│   └── agent_pascal.py       # Agent de recherche web
│
├── api/                       # 🌐 API REST
│   ├── __init__.py
│   ├── routes.py             # Endpoints FastAPI
│   └── models.py             # Modèles Pydantic
│
├── config/                    # ⚙️ Configuration
│   ├── __init__.py
│   └── settings.py           # Variables d'environnement
│
├── services/                  # 🔧 Services métier
│   ├── __init__.py
│   ├── memory_service.py     # Gestion de la mémoire
│   └── search_service.py     # Recherche web (Tavily)
│
├── utils/                     # 🛠️ Utilitaires
│   ├── __init__.py
│   └── helpers.py            # Fonctions helper
│
├── data/                      # 💾 Base de données
│   ├── .gitkeep
│   └── koffi_memory.db       # SQLite (ignoré par git)
│
├── main.py                    # 🚀 Point d'entrée
├── requirements.txt           # 📦 Dépendances
├── run.sh                     # 🏃 Script de démarrage
├── test_structure.py          # 🧪 Tests de structure
├── .env                       # 🔐 Variables d'environnement
├── .env.example              # 📝 Exemple de config
├── .gitignore                # 🚫 Fichiers ignorés
├── README.md                 # 📖 Documentation
└── LICENSE                   # ⚖️ Licence
```

## 🔄 Changements Effectués

### ✅ Nettoyage
- ❌ Supprimé le dossier `koffi/` (structure imbriquée inutile)
- ❌ Supprimé tous les fichiers de documentation obsolètes
- ❌ Supprimé les fichiers `__pycache__`
- ❌ Supprimé `utils.py` à la racine (remplacé par `utils/helpers.py`)
- ❌ Supprimé les scripts obsolètes (Makefile, start.sh, etc.)

### ✅ Réorganisation
- ✅ Déplacé tous les modules utiles directement dans `backend/`
- ✅ Corrigé tous les imports pour la nouvelle structure
- ✅ Créé une architecture modulaire claire
- ✅ Ajouté un script de démarrage `run.sh`
- ✅ Ajouté un script de test `test_structure.py`
- ✅ Mis à jour le `.gitignore`
- ✅ Créé une documentation claire

## 🎯 Avantages de la Nouvelle Structure

1. **Clarté** : Chaque module a un rôle bien défini
2. **Maintenabilité** : Facile de trouver et modifier du code
3. **Scalabilité** : Simple d'ajouter de nouveaux agents ou services
4. **Testabilité** : Structure modulaire facilite les tests
5. **Imports simples** : Plus de confusion avec les chemins d'import

## 🚀 Utilisation

### Démarrage rapide
```bash
cd backend
./run.sh
```

### Test de la structure
```bash
cd backend
python test_structure.py
```

### Développement
```bash
cd backend
source venv/bin/activate
python main.py
```

## 📝 Notes Importantes

- Tous les imports utilisent maintenant des chemins relatifs depuis `backend/`
- Le fichier `.env` doit être à la racine de `backend/`
- La base de données SQLite est dans `backend/data/`
- Les `__pycache__` sont automatiquement ignorés par git

## 🔗 Intégration Frontend

Le frontend Next.js communique avec le backend via :
- URL: `http://localhost:8000`
- Endpoint principal: `POST /chat`
- Headers: `x-session-id` pour la gestion des sessions

## ✨ Prochaines Étapes

1. Tester le serveur avec `./run.sh`
2. Vérifier que le frontend se connecte correctement
3. Tester les fonctionnalités de mémoire
4. Tester la recherche web avec agent_pascal
