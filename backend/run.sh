#!/bin/bash

# Script de démarrage pour KOFFI Agent

echo "🚀 Démarrage de KOFFI Agent..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installation des dépendances..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
    echo "✅ Dépendances installées"
fi

# Lancer le serveur
echo "🌐 Lancement du serveur..."
python main.py
