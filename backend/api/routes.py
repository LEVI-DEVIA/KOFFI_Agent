"""
Routes FastAPI pour KOFFI Agent
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Ajouter le dossier backend au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from api.models import ChatRequest, ChatResponse, Message
from services.memory_service import memory_service
from utils.helpers import extract_content
from config.settings import STREAMING_WORD_DELAY


# Variable globale pour l'agent (sera initialisée dans main.py)
agent = None


def set_agent(agent_instance):
    """Définit l'agent global"""
    global agent
    agent = agent_instance


def setup_routes(app: FastAPI):
    """Configure toutes les routes de l'application"""

    # Middleware pour gérer les sessions utilisateur
    @app.middleware("http")
    async def add_user_session_middleware(request: Request, call_next):
        user_id = request.headers.get("x-session-id", "default_user")
        request.state.user_id = user_id
        print(f"🔄 Session utilisateur: {user_id}")
        response = await call_next(request)
        return response

    # Endpoint principal de chat
    @app.post("/chat")
    async def chat_endpoint(chat_request: ChatRequest, request: Request):
        try:
            print(
                f"📨 Requête reçue: {len(chat_request.messages) if chat_request.messages else 0} messages"
            )

            user_id = getattr(request.state, "user_id", "default_user")
            session_id = memory_service.get_or_create_session(
                "koffi_langgraph_app", user_id
            )
            print(f"💾 Session: {session_id}")

            memory_context = memory_service.get_memory_context(session_id)

            if not chat_request.messages or len(chat_request.messages) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Messages array is required and cannot be empty",
                )

            lc_messages = []
            if memory_context:
                lc_messages.append(
                    SystemMessage(content=f"Contexte de mémoire:\n{memory_context}")
                )

            for msg in chat_request.messages:
                if msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            config = {
                "configurable": {
                    "thread_id": f"thread_{user_id}",
                }
            }

            if chat_request.stream:
                return StreamingResponse(
                    generate_stream(lc_messages, config, session_id),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )
            else:
                return await generate_normal_response(
                    lc_messages, config, session_id, user_id
                )

        except Exception as e:
            import traceback

            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            print(f"❌ Erreur: {error_detail}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_stream(lc_messages, config, session_id):
        """Génère un stream de réponse mot par mot"""
        try:
            user_message = None
            for message in reversed(lc_messages):
                if isinstance(message, HumanMessage):
                    user_message = message
                    break

            print(
                f"🤖 Appel de l'agent (invoke) pour streaming simulé avec {len(lc_messages)} messages..."
            )

            # Utiliser invoke pour obtenir la réponse complète
            result = await agent.ainvoke({"messages": lc_messages}, config=config)
            print(f"✅ Réponse reçue: {len(result['messages'])} messages")

            # Extraire la réponse
            ai_response = None
            for message in reversed(result["messages"]):
                if isinstance(message, AIMessage):
                    ai_response = message
                    break

            if not ai_response:
                raise ValueError("Aucune réponse de l'assistant trouvée")

            # Extraire le contenu
            full_response = extract_content(ai_response)
            print(f"📝 Contenu extrait: {len(full_response)} caractères")

            # Simuler le streaming en envoyant mot par mot
            words = full_response.split()
            for i, word in enumerate(words):
                content_to_send = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'content': content_to_send, 'type': 'content'})}\n\n"
                await asyncio.sleep(STREAMING_WORD_DELAY)

            # Mettre à jour la mémoire
            if user_message:
                user_content = extract_content(user_message)
                memory_service.update_conversation_memory(
                    session_id, user_content, full_response
                )

            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            print(f"✅ Streaming terminé: {len(full_response)} caractères envoyés")

        except Exception as e:
            import traceback

            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            print(f"❌ Erreur streaming: {error_detail}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    async def generate_normal_response(lc_messages, config, session_id, user_id):
        """Génère une réponse normale (sans streaming)"""
        print(f"🤖 Appel de l'agent avec {len(lc_messages)} messages...")
        result = await agent.ainvoke({"messages": lc_messages}, config=config)
        print(f"✅ Réponse reçue de l'agent: {len(result['messages'])} messages")

        ai_response = None
        user_message = None

        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage) and ai_response is None:
                ai_response = message
            if isinstance(message, HumanMessage) and user_message is None:
                user_message = message
            if ai_response and user_message:
                break

        if not ai_response:
            raise ValueError("Aucune réponse de l'assistant trouvée")

        content = extract_content(ai_response)

        if isinstance(content, str):
            lines = [line.strip() for line in content.split("\n")]
            content = "\n".join(line for line in lines if line)

        if user_message:
            user_content = extract_content(user_message)
            memory_service.update_conversation_memory(session_id, user_content, content)

        print(f"📤 Envoi de la réponse: {len(content)} caractères")

        return ChatResponse(
            message=Message(role="assistant", content=content.strip()),
            metadata={
                "model": "gemini-2.5-flash",
                "tokens_used": len(content.split()),
                "message_count": len(result["messages"]),
                "session_id": session_id,
                "user_id": user_id,
            },
        )

    # Endpoint de santé
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "model": "gemini-2.5-flash",
            "subagents": ["agent_pascal"],
            "memory": "enabled",
        }

    # Endpoints de gestion de la mémoire
    @app.post("/memory-test")
    async def test_memory(request: Request):
        """Test des fonctionnalités de mémoire"""
        try:
            user_id = getattr(request.state, "user_id", "test_user")
            session_id = memory_service.get_or_create_session(
                "koffi_langgraph_app", user_id
            )
            context = memory_service.get_memory_context(session_id)

            return {
                "status": "success",
                "session_id": session_id,
                "user_id": user_id,
                "memory_context": context,
                "message": "Memory service is working",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/add-fact")
    async def add_important_fact(fact: str, request: Request):
        """Ajouter un fait important à la mémoire"""
        try:
            user_id = getattr(request.state, "user_id", "default_user")
            session_id = memory_service.get_or_create_session(
                "koffi_langgraph_app", user_id
            )
            memory_service.add_important_fact(session_id, fact)

            return {
                "status": "success",
                "message": f"Fait ajouté: {fact}",
                "session_id": session_id,
                "user_id": user_id,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/clear-memory")
    async def clear_memory(request: Request):
        """Effacer la mémoire d'un utilisateur"""
        try:
            user_id = getattr(request.state, "user_id", "default_user")
            session_id = memory_service.get_or_create_session(
                "koffi_langgraph_app", user_id
            )
            memory_service.clear_memory(session_id)

            return {
                "status": "success",
                "message": "Mémoire effacée",
                "session_id": session_id,
                "user_id": user_id,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/memory-status")
    async def memory_status():
        """Statut du système de mémoire"""
        return {
            "status": "active",
            "memory_service": "active",
            "checkpointer": "AsyncSqliteSaver",
        }

    # Endpoint de debug
    @app.post("/chat/debug")
    async def chat_debug(chat_request: ChatRequest, request: Request):
        """Endpoint de debug pour voir la structure complète de la réponse"""
        try:
            user_id = getattr(request.state, "user_id", "default_user")

            lc_messages = []
            for msg in chat_request.messages:
                if msg.role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))

            config = {
                "configurable": {
                    "thread_id": f"thread_{user_id}",
                }
            }

            result = await agent.ainvoke({"messages": lc_messages}, config=config)

            return {
                "user_id": user_id,
                "message_count": len(result["messages"]),
                "messages": [
                    {
                        "type": type(msg).__name__,
                        "content": (
                            str(msg.content)[:200] + "..."
                            if len(str(msg.content)) > 200
                            else str(msg.content)
                        ),
                    }
                    for msg in result["messages"]
                ],
                "full_result": str(result)[:500],
            }
        except Exception as e:
            return {"error": str(e)}
