# memory_service.py
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class MemoryService:
    def __init__(self, db_path: str = "koffi_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table pour les sessions utilisateur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table pour la mémoire de conversation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            # Table pour les faits importants
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS important_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
                )
            ''')
            
            conn.commit()
    
    def get_or_create_session(self, app_name: str, user_id: str) -> str:
        """Crée ou récupère une session utilisateur"""
        session_id = f"{app_name}_{user_id}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifie si la session existe
            cursor.execute(
                "SELECT session_id FROM user_sessions WHERE session_id = ?",
                (session_id,)
            )
            
            if not cursor.fetchone():
                # Crée une nouvelle session
                cursor.execute(
                    "INSERT INTO user_sessions (session_id, user_id) VALUES (?, ?)",
                    (session_id, user_id)
                )
                conn.commit()
            else:
                # Met à jour la date d'accès
                cursor.execute(
                    "UPDATE user_sessions SET last_accessed = CURRENT_TIMESTAMP WHERE session_id = ?",
                    (session_id,)
                )
                conn.commit()
        
        return session_id
    
    def update_conversation_memory(self, session_id: str, user_message: str, assistant_message: str) -> None:
        """Ajoute un échange de conversation à la mémoire"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_memory (session_id, user_message, assistant_message) VALUES (?, ?, ?)",
                (session_id, user_message, assistant_message)
            )
            conn.commit()
    
    def get_memory_context(self, session_id: str, max_messages: int = 10) -> str:
        """Récupère le contexte de mémoire pour une session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Récupère les derniers messages de conversation
            cursor.execute(
                "SELECT user_message, assistant_message FROM conversation_memory "
                "WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, max_messages)
            )
            messages = cursor.fetchall()
            
            # Récupère les faits importants
            cursor.execute(
                "SELECT fact FROM important_facts WHERE session_id = ?",
                (session_id,)
            )
            facts = [row[0] for row in cursor.fetchall()]
        
        # Formate le contexte
        context_parts = []
        
        if facts:
            context_parts.append("### Faits importants:")
            context_parts.extend([f"- {fact}" for fact in facts])
            context_parts.append("")
        
        if messages:
            context_parts.append("### Historique de la conversation:")
            for user_msg, asst_msg in reversed(messages):
                context_parts.append(f"Utilisateur: {user_msg}")
                context_parts.append(f"Assistant: {asst_msg}")
                context_parts.append("")
        
        return "\n".join(context_parts).strip()
    
    def add_important_fact(self, session_id: str, fact: str) -> None:
        """Ajoute un fait important à la mémoire"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO important_facts (session_id, fact) VALUES (?, ?)",
                (session_id, fact)
            )
            conn.commit()
    
    def clear_memory(self, session_id: str) -> None:
        """Efface la mémoire d'une session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_memory WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM important_facts WHERE session_id = ?", (session_id,))
            conn.commit()

# Instance globale du service de mémoire
memory_service = MemoryService()

# Pour une utilisation avec LangGraph
def get_memory_checkpointer():
    return memory_service

# Pour une utilisation directe
def get_memory_service() -> MemoryService:
    return memory_service