import re

def clean_text(text):
    """
    Nettoie le texte :
    - minuscule
    - suppression caractères spéciaux
    """
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


