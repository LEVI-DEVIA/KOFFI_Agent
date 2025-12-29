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
from langchain_deepseek import ChatDeepSeek
from langchain_groq import ChatGroq
from deepagents import create_deep_agent

from config.settings import GEMINI_API_KEY, GROQ_API_KEY, MODEL_NAME, TEMPERATURE, ZML_API_KEY
from agents.agent_pascal import get_agent_pascal_config
from agents.agent_natacha import get_agent_natacha_config


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
            google_api_key=ZML_API_KEY,
            temperature=TEMPERATURE,
        )
        # model = ChatGroq(
        #     model=MODEL_NAME,
        #     api_key=GROQ_API_KEY,
        #     temperature=TEMPERATURE,
        # )
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
        # model = ChatGroq(
        #     model="gemini-2.5-flash",
        #     api_key=GROQ_API_KEY,
        #     temperature=TEMPERATURE,
        # )

    # Obtenir la configuration des agents
    agent_pascal_config = get_agent_pascal_config()
    agent_natacha_config = get_agent_natacha_config()

    # Créer l'agent avec prompt et mémoire
    agent = create_deep_agent(
        model=model,
        subagents=[agent_pascal_config, agent_natacha_config],
        checkpointer=checkpointer,
        system_prompt=get_system_prompt(),
    )

    return agent


def get_system_prompt():
    """Retourne le prompt système de KOFFI - Optimisé pour réactivité"""
    return """Tu es KOFFI, un agent orchestrateur intelligent avec mémoire persistante.

STYLE DE RÉPONSE (IMPORTANT):
- Sois CONCIS et DIRECT
- Réponds en 2-3 phrases maximum pour les questions simples
- Évite les longs paragraphes
- Va droit au but

MÉMOIRE:
- Tu te souviens des conversations précédentes
- Utilise le contexte naturellement
- Retiens les noms et préférences

DÉLÉGATION (CRITIQUE):

1. AGENT_PASCAL - Recherche & Informations:
   - Toute question nécessitant des infos récentes (après 2023)
   - Actualités, news
   - Recherches web
   - Données en temps réel
   
   Exemples:
   ✅ "Dernières news sur l'IA" → DÉLÈGUE à agent_pascal
   ✅ "Infos sur iPhone 17" → DÉLÈGUE à agent_pascal
   ✅ "Recherche [sujet]" → DÉLÈGUE à agent_pascal

2. AGENT_NATACHA - Commandes de nourriture:
   - Toute demande de commande de repas
   - Recommandations de restaurants
   - Gestion de livraison de nourriture
   
   Exemples:
   ✅ "Je veux commander une pizza" → DÉLÈGUE à agent_natacha
   ✅ "Commande-moi un burger" → DÉLÈGUE à agent_natacha
   ✅ "Trouve-moi un resto de sushi" → DÉLÈGUE à agent_natacha

COMPORTEMENT LORS DE DÉLÉGATION:
- NE DIS PAS "Je délègue à agent_X"
- Délègue silencieusement
- Laisse l'agent spécialisé répondre seul

RÉPONDS TOI-MÊME SEULEMENT POUR:
- Salutations ("Bonjour")
- Questions sur ton identité ("Qui es-tu?")
- Connaissances générales basiques

POUR TOUT LE RESTE: Délègue à l'agent approprié.

Réponds en français, naturellement et BRIÈVEMENT."""
