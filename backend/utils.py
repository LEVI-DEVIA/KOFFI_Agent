import asyncio
from typing import Any, Dict, List
from google.adk.runners import Runner


async def call_agent_async(runner: Runner, user_id: str, session_id: str, user_input: str) -> Dict[str, Any]:
    """
    Appelle l'agent de manière asynchrone et retourne la réponse
    """
    try:
        # Créer le message utilisateur
        messages = [
            {
                "role": "user",
                "content": user_input,
                "id": f"msg_{asyncio.get_event_loop().time()}"
            }
        ]
        
        # Exécuter l'agent
        result = await runner.run_async(
            user_id=user_id,
            session_id=session_id,
            messages=messages,
            tools=[],
            context=[],
        )
        
        # Extraire la réponse
        if result and hasattr(result, 'messages'):
            assistant_messages = [msg for msg in result.messages if msg.get('role') == 'assistant']
            if assistant_messages:
                return {
                    "success": True,
                    "response": assistant_messages[-1].get('content', ''),
                    "full_result": result
                }
        
        return {
            "success": False,
            "response": "Aucune réponse de l'agent",
            "full_result": result
        }
        
    except Exception as e:
        print(f"Erreur lors de l'appel à l'agent: {e}")
        return {
            "success": False,
            "response": f"Erreur: {str(e)}",
            "error": str(e)
        }


def print_agent_response(result: Dict[str, Any]) -> None:
    """
    Affiche la réponse de l'agent de manière formatée
    """
    if result.get("success"):
        print(f"Agent: {result['response']}")
    else:
        print(f"Erreur: {result.get('response', 'Erreur inconnue')}")