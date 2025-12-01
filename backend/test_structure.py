#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les imports fonctionnent
"""

import sys
from pathlib import Path

# Ajouter le dossier backend au path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("🧪 Test de la structure du backend...\n")

# Test 1: Config
print("1️⃣ Test des imports de config...")
try:
    from config.settings import HOST, PORT, GEMINI_API_KEY, TAVILY_API_KEY
    print(f"   ✅ Config OK - Host: {HOST}, Port: {PORT}")
except Exception as e:
    print(f"   ❌ Erreur config: {e}")
    sys.exit(1)

# Test 2: Services
print("\n2️⃣ Test des imports de services...")
try:
    from services.memory_service import memory_service
    from services.search_service import search_web
    print("   ✅ Services OK")
except Exception as e:
    print(f"   ❌ Erreur services: {e}")
    sys.exit(1)

# Test 3: Utils
print("\n3️⃣ Test des imports d'utilitaires...")
try:
    from utils.helpers import extract_content
    print("   ✅ Utils OK")
except Exception as e:
    print(f"   ❌ Erreur utils: {e}")
    sys.exit(1)

# Test 4: API
print("\n4️⃣ Test des imports d'API...")
try:
    from api.models import ChatRequest, ChatResponse, Message
    from api import routes
    print("   ✅ API OK")
except Exception as e:
    print(f"   ❌ Erreur API: {e}")
    sys.exit(1)

# Test 5: Agents
print("\n5️⃣ Test des imports d'agents...")
try:
    from agents.agent_pascal import get_agent_pascal_config
    from agents.koffi_agent import create_koffi_agent, get_system_prompt
    print("   ✅ Agents OK")
except Exception as e:
    print(f"   ❌ Erreur agents: {e}")
    sys.exit(1)

# Test 6: Main
print("\n6️⃣ Test de l'import du main...")
try:
    # On ne peut pas importer main directement car il lance uvicorn
    # Mais on peut vérifier que le fichier existe et est valide
    main_path = backend_dir / "main.py"
    if main_path.exists():
        print("   ✅ Main.py existe")
    else:
        print("   ❌ Main.py introuvable")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erreur main: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ Tous les tests sont passés avec succès!")
print("="*50)
print("\n💡 Pour lancer le serveur:")
print("   ./run.sh")
print("   ou")
print("   python main.py")
