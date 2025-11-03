#!/usr/bin/env python3
"""
Script pour vérifier le quota de l'API Google Gemini
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv("koffi/.env")

def check_api_quota():
    """
    Vérifie le statut de l'API et les quotas
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY non trouvée dans .env")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        # Configurer l'API
        genai.configure(api_key=api_key)
        
        # Lister les modèles disponibles
        print("\n📋 Modèles disponibles:")
        models = genai.list_models()
        
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"  ✅ {model.name}")
                if hasattr(model, 'rate_limit'):
                    print(f"     Limite: {model.rate_limit}")
        
        # Test simple
        print("\n🧪 Test simple de l'API...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Dis juste 'Bonjour' en français")
        print(f"✅ Réponse: {response.text}")
        
        print("\n✅ API fonctionnelle - pas de problème de quota pour l'instant")
        
    except Exception as e:
        error_str = str(e)
        
        if "429" in error_str or "Too Many Requests" in error_str:
            print("🚨 QUOTA DÉPASSÉ!")
            print("Solutions:")
            print("  1. Attendre quelques minutes/heures")
            print("  2. Vérifier les limites sur https://console.cloud.google.com/")
            print("  3. Utiliser un autre modèle (gemini-1.5-flash au lieu de gemini-2.0-flash-exp)")
            
        elif "403" in error_str or "Forbidden" in error_str:
            print("🚨 ACCÈS REFUSÉ!")
            print("  - Vérifier que l'API Gemini est activée")
            print("  - Vérifier la clé API")
            
        else:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_quota()