# Installation des dépendances
install-packages:
	pip install -r requirements.txt

# Lancer le serveur ADK
run:
	adk web

# Créer un environnement virtuel
create-venv:
	python -m venv venv

# Activer l'environnement virtuel (à exécuter avec: source venv/bin/activate)
activate-venv:
	@echo "Run: source venv/bin/activate"

# Sauvegarder les dépendances
save:
	pip freeze > requirements.txt

# Nettoyer les fichiers temporaires
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Aide
help:
	@echo "Commandes disponibles:"
	@echo "  make install-packages  - Installer les dépendances"
	@echo "  make run              - Lancer le serveur ADK"
	@echo "  make create-venv      - Créer un environnement virtuel"
	@echo "  make save             - Sauvegarder les dépendances"
	@echo "  make clean            - Nettoyer les fichiers temporaires"