from fastapi import FastAPI, HTTPException
import joblib
from pydantic import BaseModel

try:
    model_mini = joblib.load("src/model_sauvegarde/model_minibert.joblib")
    model_tfd = joblib.load("src/model_sauvegarde/model_tfi.joblib")
except Exception as e:
    print("Erreur chargement modèles:", e)
    model_mini = None
    model_tfd = None


a = model_mini.recommend("Python java Machine Learning SQL DBT html postgresql\
   css\
   mongodb\
   mysql\
   javascript", "Dakar", 0
   )
b = model_tfd.predict('JAva', "Dakar")


# from fastapi import FastAPI, 
# from pydantic import BaseModel
# import joblib

# # --- Load models ---
# model_mini = joblib.load("/app/src/model_sauvegarde/model_minibert.joblib")
# model_tfd  = joblib.load("/app/src/model_sauvegarde/model_tfi.joblib")

# --- Schemas ---
class Item_tfidf(BaseModel):
    competences: str
    region: str

class Item_minibert(BaseModel):
    competences: str
    region: str
    experience: int

# --- App ---
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API fonctionne 🚀"}

# ── TF-IDF vectoriel ──────────────────────────────────────────
@app.post("/Recomendation_vectoriel")
def get_recommendation_vectoriel(item: Item_tfidf):
    try:
        result = model_tfd.predict(item.competences, item.region)
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/Recomendation_vectoriel")
def get_recommendation_vectoriel_info():
    return {"message": "Utilisez POST avec {competences, region}"}

# ── MiniBERT ──────────────────────────────────────────────────
@app.post("/Recomendation_bert")
def get_recommendation_bert(item: Item_minibert):
    try:
        result = model_mini.recommend(item.competences, item.region, item.experience)
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/Recomendation_bert")
def get_recommendation_bert_info():
    return {"message": "Utilisez POST avec {competences, region, experience}"}