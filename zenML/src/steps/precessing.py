from zenml.steps import step

from ..utils.parse_experience import parse_experience


@step
def precessing(dt):
    dt["experience_clean"] = dt["experience"].apply(parse_experience)
    grouped = dt.groupby(["poste", "region", "experience_clean"])["competence"] \
                    .apply(lambda x: " ".join(x)).dropna().reset_index()
    data_grouped = grouped.rename(columns={
    "competence": "competence_clean",
    "region": "region_clean",
    "experience_clean": "experience"
    })
    return data_grouped