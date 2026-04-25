import re
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from zenml.steps import step 
from ..utils.compet_duplique import deduplicate_skills
import joblib

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()



class RecommendationEmploi:

    def __init__(self):
        self.model_emb = SentenceTransformer("all-MiniLM-L6-v2")
        self.df = None
        self.embeddings = None

    def fit(self, df: pd.DataFrame):

        required_cols = ["poste", "competence_clean", "region_clean", "experience"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}")

        df = df.copy()

        # nettoyage
        df["competence_clean"] = df["competence_clean"].apply(clean_text).apply(deduplicate_skills)
        df["region_clean"] = df["region_clean"].apply(clean_text)

        # profil enrichi
        df["job_profile"] = (
            df["poste"].fillna("") + " | " +
            df["competence_clean"] + " | " +
            df["region_clean"] + " | " +
            df["experience"].astype(str)
        )

        self.embeddings = self.model_emb.encode(df["job_profile"].tolist())
        self.df = df.reset_index(drop=True)

        return self

    # -----------------------------
    # SCORES
    # -----------------------------
    def experience_score(self, user_exp, job_exp):
        max_exp = self.df["experience"].max()
        diff = abs(user_exp - job_exp)
        return 1 - (diff / max_exp)

    def region_score(self, user_region, job_region):
        if user_region == job_region:
            return 1.0
        elif user_region in job_region or job_region in user_region:
            return 0.7
        return 0.3

    # -----------------------------
    # SKILLS
    # -----------------------------
    def missing_skills(self, user_skills, job_skills):
        user_set = set(user_skills.split())
        job_set = set(job_skills.split())
        return list(job_set - user_set)

    # -----------------------------
    # RECOMMEND
    # -----------------------------
    def recommend(self, skills, region, experience, top_k=5):

        user_text = clean_text(skills)
        user_region = clean_text(region)

        #  profil utilisateur complet
        user_profile = f"{user_text} | {user_region} | {experience}"

        user_emb = self.model_emb.encode(user_profile)

        skill_scores = cosine_similarity([user_emb], self.embeddings)[0]

        exp_scores = np.array([
            self.experience_score(experience, e)
            for e in self.df["experience"]
        ])

        region_scores = np.array([
            self.region_score(user_region, r)
            for r in self.df["region_clean"]
        ])

        final_scores = (
            0.65 * skill_scores +
            0.20 * exp_scores +
            0.15 * region_scores
        )

        top_idx = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for idx in top_idx:
            row = self.df.iloc[idx]

            results.append({
                "poste": row["poste"],
                "region": row["region_clean"],
                "score": round(float(final_scores[idx]), 4),
                "missing_skills": self.missing_skills(
                    user_text,
                    row["competence_clean"]
                )
            })

        return results
    


@step
def Deuxieme_modele(df) -> str:
    model = RecommendationEmploi()
    model.fit(df)

    path = "model_minibert.joblib"
    joblib.dump(model, path)

    return path