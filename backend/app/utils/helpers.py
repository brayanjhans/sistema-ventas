import re
from typing import Optional

def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    Example: "Electrónica y Tecnología" -> "electronica-y-tecnologia"
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spanish characters
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any character that isn't alphanumeric or space
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[\s-]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text
