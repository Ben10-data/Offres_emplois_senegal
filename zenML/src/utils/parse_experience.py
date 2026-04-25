def parse_experience(exp):
    """
    Convertit une chaîne d'expérience en valeur numérique (années)
    """
    if not isinstance(exp, str):
        return 0.0
    
    exp = exp.lower().strip()
    
    mapping = {
        "etudiant": 0.0,
        "jeune diplômé": 0.3,
        "jeune diplômé et plus": 0.6,
        "débutant < 2 ans": 1.0,
        "débutant < 2 ans et plus": 1.6,
        "expérience entre 2 ans et 5 ans": 2.0,
        "expérience entre 2 ans et 5 ans et plus": 3.0,
        "expérience entre 5 ans et 10 ans": 5.0,
        "expérience > 10 ans": 10.0
    }
    
    # Nettoyer la chaîne pour correspondre au mapping
    # Remplacer les caractères spéciaux
    exp = exp.replace("'", "")
    
    # Chercher la correspondance exacte
    if exp in mapping:
        return mapping[exp]
    
    # Gestion des cas particuliers avec des mots-clés
    if "jeune diplômé" in exp:
        if "plus" in exp:
            return 0.6
        return 0.3
    elif "débutant" in exp or "etudiant" in exp and "2 ans" in exp:
        if "plus" in exp:
            return 1.6
        return 1.0
    elif "2 ans et 5 ans" in exp:
        if "plus" in exp:
            return 3.0
        return 2.0
    elif "5 ans et 10 ans" in exp:
        return 5.0
    elif "10 ans" in exp:
        return 10.0
    elif "etudiant" in exp:
        return 0.0
    
    # Valeur par défaut
    return 0.0