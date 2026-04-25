from zenml.steps import step
from ..utils.clean_text import clean_text
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack
import joblib

class TfidfJobModel:
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.encoder = OneHotEncoder()
        self.model = LogisticRegression(max_iter=1000)

    def fit(self, df):

        df["text"] = df["competence_clean"] + " " + df["region_clean"]

        X_text = self.vectorizer.fit_transform(df["text"])
        X_region = self.encoder.fit_transform(df[["region_clean"]])

        X = hstack([X_text, X_region])
        y = df["poste"]

        self.model.fit(X, y)
        return self  

    def predict(self, skills, region):
        """
        Prédit un poste à partir des skills + région
        """
        text = clean_text(skills + " " + region)

        X_text = self.vectorizer.transform([text])
        X_region = self.encoder.transform([[clean_text(region)]])

        X = hstack([X_text, X_region])

        return self.model.predict(X)[0]



@step 
def Premier_model(df):
    model_instance = TfidfJobModel()
    model_instance.fit(df)

    path = "model_tfi.joblib"
    joblib.dump(model_instance, path)
    
    return model_instance