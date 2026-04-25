from zenml.steps import step
import re 

from ..utils.clean_text import clean_text

@step
def prepare_data(df):

    data = df[['poste', 'competence', 'region', 'experience']].copy()
    # nettoyage
    data["competence_clean"] = data["competence"].apply(clean_text)
    data["region_clean"] = data["region"].apply(clean_text)

    # regroupement (IMPORTANT)
    grouped = data.groupby(["poste", "region_clean"])["competence_clean"] \
                  .apply(lambda x: " ".join(x)).dropna().reset_index()

    # moyenne expérience
    exp = data.groupby(["poste", "region_clean"])["experience"] \
                      .apply(lambda x: " ".join(x)).dropna().reset_index()

    grouped = grouped.merge(exp, on=["poste", "region_clean"])

    return grouped