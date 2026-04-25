import pandas as pd 


def deduplicate_skills(text):
    if pd.isna(text):
        return ""
    words = text.split()
    return " ".join(dict.fromkeys(words)) 