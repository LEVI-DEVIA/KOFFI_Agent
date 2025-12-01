# Commandes Utiles - KOFFI Backend

## 🚀 Démarrage

### Première installation
```bash
cd backend
./run.sh
```
Le script `run.sh` va automatiquement :
1. Créer l'environnement virtuel
2. Installer les dépendances
3. Lancer le serveur

### Démarrage rapide (après installation)
```bash
cd backend
./run.sh
```

### Démarrage manuel
```bash
cd backend
source venv/bin/activate
python main.py
```

## 🧪 Tests

### Tester la structure
```bash
cd backend
python test_structure.py
```

### Tester l'API
```bash
# Health check
curl http://localhost:8000/health

# Test de mémoire
curl -X POST http://localhost:8000/memory-test \
  -H "x-session-id: test_user"

# Chat simple
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

## 🔧 Développement

### Activer l'environnement virtuel
```bash
cd backend
source venv/bin/activate
```

### Installer une nouvelle dépendance
```bash
pip install nom_du_package
pip freeze > requirements.txt
```

### Désactiver l'environnement virtuel
```bash
deactivate
```

## 🧹 Nettoyage

### Nettoyer les fichiers Python
```bash
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find backend -type f -name "*.pyc" -delete
```

### Nettoyer la base de données
```bash
rm -f backend/data/koffi_memory.db*
```

### Réinstaller l'environnement
```bash
rm -rf backend/venv
cd backend
./run.sh
```

## 📊 Monitoring

### Voir les logs en temps réel
```bash
cd backend
python main.py
# Les logs s'affichent dans le terminal
```

### Accéder à la documentation API
```
http://localhost:8000/docs
```

## 🐛 Debugging

### Vérifier les imports
```bash
cd backend
python test_structure.py
```

### Vérifier les variables d'environnement
```bash
cd backend
cat .env
```

### Tester un module spécifique
```bash
cd backend
source venv/bin/activate
python -c "from agents.koffi_agent import create_koffi_agent; print('OK')"
```

## 📦 Gestion des Dépendances

### Voir les dépendances installées
```bash
pip list
```

### Mettre à jour une dépendance
```bash
pip install --upgrade nom_du_package
pip freeze > requirements.txt
```

### Vérifier les dépendances obsolètes
```bash
pip list --outdated
```

## 🔐 Sécurité

### Vérifier que .env n'est pas commité
```bash
git status
# .env ne doit PAS apparaître dans les fichiers à commiter
```

### Créer un nouveau .env depuis l'exemple
```bash
cp backend/.env.example backend/.env
# Puis éditer backend/.env avec vos vraies clés API
```

## 🌐 Production

### Lancer avec Gunicorn (production)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Lancer avec Docker (si configuré)
```bash
docker build -t koffi-backend .
docker run -p 8000:8000 koffi-backend
```
