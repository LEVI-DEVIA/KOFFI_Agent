#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement des sessions multiples
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_session(session_id: str, message: str):
    """Teste une session spécifique"""
    print(f"\n🧪 Test session {session_id}")
    print(f"📝 Message: {message}")
    
    payload = {
        "threadId": f"memory_thread_{session_id}",
        "runId": f"run_{int(time.time())}",
        "state": {},
        "messages": [
            {
                "id": f"msg_{int(time.time())}",
                "role": "user",
                "content": message,
            }
        ],
        "tools": [],
        "context": [],
        "forwardedProps": {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-session-id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/", json=payload, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Lire la réponse streamée
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Enlever 'data: '
                            if data.get('type') == 'TEXT_MESSAGE_CONTENT' and data.get('delta'):
                                full_response += data['delta']
                        except json.JSONDecodeError:
                            continue
            
            print(f"✅ Réponse: {full_response[:100]}...")
            return full_response
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def check_sessions():
    """Vérifie les sessions actives"""
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Sessions actives: {data['total_sessions']}")
            for session_id in data['active_sessions']:
                print(f"  - {session_id}")
        else:
            print(f"❌ Erreur lors de la vérification des sessions: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    print("🚀 Test des sessions multiples pour Koffi")
    print("=" * 50)
    
    # Test avec différentes sessions
    sessions_tests = [
        ("session_alice", "Bonjour, je m'appelle Alice"),
        ("session_bob", "Salut, moi c'est Bob"),
        ("session_alice", "Tu te souviens de mon nom ?"),
        ("session_bob", "Quel est mon nom déjà ?"),
        ("session_charlie", "Hey, je suis Charlie, nouveau ici"),
        ("session_alice", "Parle-moi de Bob"),
    ]
    
    for session_id, message in sessions_tests:
        test_session(session_id, message)
        time.sleep(1)  # Petite pause entre les tests
    
    # Vérifier les sessions actives
    check_sessions()
    
    print("\n✨ Tests terminés !")

if __name__ == "__main__":
    main()