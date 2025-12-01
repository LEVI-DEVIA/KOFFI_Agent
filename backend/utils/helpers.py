"""
Fonctions utilitaires
"""


def extract_content(message):
    """Extrait le contenu texte d'un message LangChain de manière robuste."""
    if hasattr(message, "content"):
        content = message.content
    else:
        content = message

    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    text_parts.append(item["text"])
                elif "content" in item:
                    text_parts.append(str(item["content"]))
        return " ".join(text_parts)
    elif isinstance(content, dict):
        if "text" in content:
            return content["text"]
        elif "content" in content:
            return content["content"]
        else:
            return str(content)

    return str(content)
