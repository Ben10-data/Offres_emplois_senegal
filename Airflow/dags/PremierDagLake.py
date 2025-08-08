from airflow import DAG
from airflow.operators.bash import BashOperator 

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(dag_id="Premier_dag", 
    start_date=datetime(2025,7,28), 
    schedule_interval=None,catchup=False, 
    description="Automatisation " \
    "d\' un pipeline de scraping jusqu' " \
    "a rapport finale") as dag:
    
    # initialisation de notre dag 
    start_etape = BashOperator(
        task_id ="premier_Etape",
        bash_command = "echo Pipeline de cette semaine -offre a tenter sa chance dans la semaine"
    )

    with TaskGroup("scraping_group",) as group_scraping:
        # On cree deux taches qui s'executer automatiquement 

        # Premiere tache de la semaine 
        tache1 = BashOperator(
            task_id = "scrap_emploi_dakar",
            bash_command = "cd /opt/airflow/scrapjob/scrapjob/spiders && scrapy crawl emploi_dakar"
        )
        # Deuxieme tache de la meme semaine 
        tache2 = BashOperator(
            task_id = "scrapy_Amploi_senegal", 
            bash_command = "cd /opt/airflow/scrapjob/scrapjob/spiders && scrapy crawl emploisenegal",
        )
    end_etape = BashOperator(
        task_id ='end', 
        bash_command = "echo fin - love and peace"
    )
    

    start_etape >> group_scraping >> end_etape
    

    

    