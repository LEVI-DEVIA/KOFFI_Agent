"""
Service de recherche web
"""
import sys
import os
from pathlib import Path

# Ajouter le dossier backend au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from config.settings import TAVILY_API_KEY


@tool
def search_web(query: str) -> str:
    """Search the web for current information and return formatted results. 
    Use this tool for ANY question about recent events, product releases, specifications, 
    news, or information that might have changed after 2023."""
    try:
        tavily_search = TavilySearchResults(
            api_key=TAVILY_API_KEY,
            max_results=5,
            search_depth="advanced",
            max_tokens=2000,
        )
        results = tavily_search.invoke(query)
        
        if not results:
            return f"Aucun résultat trouvé pour la recherche: {query}"
        
        formatted = [f"Résultats de recherche pour '{query}':\n"]
        for i, result in enumerate(results, 1):
            formatted.append(
                f"\n{i}. {result.get('title', 'Sans titre')}\n"
                f"   {result.get('content', 'Pas de description')}\n"
                f"   Source: {result.get('url', 'N/A')}"
            )
        return "\n".join(formatted)
    except Exception as e:
        return f"Erreur lors de la recherche: {str(e)}"
