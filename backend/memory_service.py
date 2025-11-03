import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv

load_dotenv()


class KoffiMemoryService:
    """
    Service de mémoire persistante pour l'agent Koffi
    """
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        
        if use_database:
            # Utiliser SQLite pour la persistance
            db_path = os.getenv("DATABASE_PATH", "./koffi_memory.db")
            db_url = f"sqlite:///{db_path}"
            self.session_service = DatabaseSessionService(db_url=db_url)
            print(f"💾 Mémoire persistante activée: {db_path}")
        else:
            # Utiliser la mémoire temporaire
            self.session_service = InMemorySessionService()
            print("🧠 Mémoire temporaire activée")
    
    def get_or_create_session(self, app_name: str, user_id: str) -> str:
        """
        Récupère une session existante ou en crée une nouvelle
        """
        try:
            # Chercher les sessions existantes
            existing_sessions = self.session_service.list_sessions(
                app_name=app_name,
                user_id=user_id,
            )
            
            if existing_sessions and len(existing_sessions.sessions) > 0:
                # Utiliser la session la plus récente
                session_id = existing_sessions.sessions[0].id
                session = self.session_service.get_session(session_id)
                
                print(f"📚 Session existante trouvée: {session_id}")
                print(f"🕒 Dernière activité: {session.updated_at}")
                
                # Afficher un résumé de la mémoire
                if session.state:
                    self._print_memory_summary(session.state)
                
                return session_id
            else:
                # Créer une nouvelle session
                initial_state = self._create_initial_state(user_id)
                new_session = self.session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    state=initial_state,
                )
                
                print(f"✨ Nouvelle session créée: {new_session.id}")
                return new_session.id
                
        except Exception as e:
            print(f"❌ Erreur lors de la gestion de session: {e}")
            # Fallback: créer une session temporaire
            return f"temp_session_{datetime.now().timestamp()}"
    
    def _create_initial_state(self, user_id: str) -> Dict[str, Any]:
        """
        Crée l'état initial pour une nouvelle session
        """
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "user_preferences": {},
            "important_facts": [],
            "reminders": [],
            "search_history": [],
            "topics_discussed": [],
        }
    
    def _print_memory_summary(self, state: Dict[str, Any]) -> None:
        """
        Affiche un résumé de ce dont l'agent se souvient
        """
        print("🧠 Mémoire de Koffi:")
        
        if state.get("conversation_history"):
            print(f"  💬 {len(state['conversation_history'])} messages en mémoire")
        
        if state.get("important_facts"):
            print(f"  📝 {len(state['important_facts'])} faits importants")
            for fact in state["important_facts"][-3:]:  # Afficher les 3 derniers
                print(f"    • {fact}")
        
        if state.get("reminders"):
            print(f"  ⏰ {len(state['reminders'])} rappels")
        
        if state.get("topics_discussed"):
            print(f"  🏷️ Sujets discutés: {', '.join(state['topics_discussed'][-5:])}")
    
    def update_conversation_memory(self, session_id: str, user_message: str, agent_response: str) -> None:
        """
        Met à jour la mémoire de conversation
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session or not session.state:
                return
            
            # Ajouter à l'historique de conversation
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "user": user_message,
                "agent": agent_response,
            }
            
            if "conversation_history" not in session.state:
                session.state["conversation_history"] = []
            
            session.state["conversation_history"].append(conversation_entry)
            
            # Garder seulement les 50 derniers messages pour éviter une base trop lourde
            if len(session.state["conversation_history"]) > 50:
                session.state["conversation_history"] = session.state["conversation_history"][-50:]
            
            # Mettre à jour la session
            self.session_service.update_session(session_id, session.state)
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la mémoire: {e}")
    
    def add_important_fact(self, session_id: str, fact: str) -> None:
        """
        Ajoute un fait important à retenir
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session or not session.state:
                return
            
            if "important_facts" not in session.state:
                session.state["important_facts"] = []
            
            fact_entry = {
                "fact": fact,
                "timestamp": datetime.now().isoformat(),
            }
            
            session.state["important_facts"].append(fact_entry)
            self.session_service.update_session(session_id, session.state)
            
            print(f"📝 Fait important ajouté: {fact}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du fait: {e}")
    
    def get_memory_context(self, session_id: str) -> str:
        """
        Génère un contexte de mémoire pour l'agent
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session or not session.state:
                return ""
            
            context_parts = []
            
            # Historique récent
            if session.state.get("conversation_history"):
                recent_history = session.state["conversation_history"][-5:]  # 5 derniers échanges
                context_parts.append("Historique récent de conversation:")
                for entry in recent_history:
                    context_parts.append(f"- Utilisateur: {entry['user']}")
                    context_parts.append(f"- Moi: {entry['agent']}")
            
            # Faits importants
            if session.state.get("important_facts"):
                context_parts.append("\nFaits importants à retenir:")
                for fact_entry in session.state["important_facts"][-10:]:  # 10 derniers faits
                    context_parts.append(f"- {fact_entry['fact']}")
            
            # Rappels
            if session.state.get("reminders"):
                context_parts.append("\nRappels actifs:")
                for reminder in session.state["reminders"]:
                    context_parts.append(f"- {reminder}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du contexte: {e}")
            return ""
    
    def clear_memory(self, session_id: str) -> None:
        """
        Efface la mémoire (pour debug ou reset)
        """
        try:
            session = self.session_service.get_session(session_id)
            if session:
                initial_state = self._create_initial_state(session.state.get("user_id", "unknown"))
                self.session_service.update_session(session_id, initial_state)
                print("🧹 Mémoire effacée")
        except Exception as e:
            print(f"❌ Erreur lors de l'effacement: {e}")


# Instance globale du service de mémoire
memory_service = KoffiMemoryService(use_database=True)