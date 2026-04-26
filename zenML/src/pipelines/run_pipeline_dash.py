from zenml.pipelines import pipeline
from ..read_data import read_data
from ..steps.prepa_data_tf import prepare_data
from ..steps.precessing import precessing
from ..steps.model2 import Deuxieme_modele
from ..steps.model1 import Premier_model


@pipeline
def pipeline_job():

    data = read_data(
        "SELECT * FROM offres_emploi_ml",
        "offres_emploi_ml",
        "dpg-d7n2vd1kh4rs73b028eg-a",
        5432,
        "offres_emploi_postgres_id4c",
        "offres_emploi_postgres_id4c_user",
        "b3HTXg7CxbbMRfeafdVxeJxNJSPa3tkv"
    )
    
    prepared = prepare_data(data)
    model = Premier_model(prepared)

    processing = precessing(data)
    modele2 = Deuxieme_modele(processing)
    


if __name__ == "__main__":
    pipeline_instance = pipeline_job()
