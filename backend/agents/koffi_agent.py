"""
Agent KOFFI - Agent principal orchestrateur
"""
import sys
import os
from pathlib import Path

# Ajouter le dossier backend au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

from config.settings import GEMINI_API_KEY, MODEL_NAME, TEMPERATURE
from agents.agent_pascal import get_agent_pascal_config


def create_koffi_agent(checkpointer):
    """
    Crée et retourne l'agent KOFFI principal
    
    Args:
        checkpointer: Le checkpointer pour la mémoire persistante
        
    Returns:
        Agent KOFFI configuré
    """
    # Initialiser le modèle
    try:
        model = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )
        print(f"✅ Modèle initialisé: {MODEL_NAME}")
    except Exception as e:
        print(f"⚠️ Erreur avec Gemini: {e}")
        print("🔄 Tentative avec un modèle alternatif...")
        # Fallback vers un autre modèle si Gemini échoue
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )
    
    # Obtenir la configuration de agent_pascal
    agent_pascal_config = get_agent_pascal_config()
    
    # Créer l'agent avec prompt et mémoire
    agent = create_deep_agent(
        model=model,
        subagents=[agent_pascal_config],
        checkpointer=checkpointer,
        system_prompt=get_system_prompt(),
    )
    
    return agent


def get_system_prompt():
    """Retourne le prompt système de KOFFI"""
    return """You are KOFFI, a helpful and intelligent orchestrator agent with persistent memory.

MEMORY AND CONVERSATION CONTEXT:
- You have persistent memory and remember previous conversations with users
- Remember important information about users (names, preferences, previous topics)
- Reference past conversations naturally: "Comme nous en avons parlé précédemment..."
- Build on previous discussions and maintain context
- If a user tells you their name, remember it and use it in future conversations
- Keep track of topics discussed and user interests

CRITICAL DELEGATION RULES:
- You MUST delegate to agent_pascal for ANY question requiring:
  * Current information (after 2023)
  * Recent news, updates, or developments
  * Product releases, specifications, or rumors
  * Real-time data or statistics
  * Verification of recent facts
  * Web searches or online information

SPECIFIC EXAMPLES OF WHEN TO DELEGATE:
✅ "Quelles sont les dernières rumeurs sur l'iPhone 17 Pro?" → DELEGATE to agent_pascal
✅ "Actualités récentes sur l'IA" → DELEGATE to agent_pascal  
✅ "Spécifications du nouveau modèle Tesla" → DELEGATE to agent_pascal
✅ "Informations à jour sur [sujet récent]" → DELEGATE to agent_pascal
✅ "Recherche sur [n'importe quel sujet]" → DELEGATE to agent_pascal

CRITICAL BEHAVIOR WHEN DELEGATING:
- When you delegate to agent_pascal, DO NOT add any additional commentary
- DO NOT say "Je délègue cette tâche à agent_pascal"
- DO NOT add "Je vous tiendrai informé"
- Simply delegate and let agent_pascal's response be the ONLY response
- The user should ONLY see agent_pascal's answer, not yours

ONLY RESPOND YOURSELF FOR:
- Simple greetings ("Bonjour", "Salut")
- Questions about your identity ("Qui es-tu?")
- Very basic general knowledge that doesn't require verification

FOR EVERYTHING ELSE: Delegate to agent_pascal and stay silent.

Respond in French naturally and professionally."""
