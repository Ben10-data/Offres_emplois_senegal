from airflow import DAG
from airflow.operators.bash import BashOperator 
from airflow.operators.python import PythonOperator

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime

from utils_BD import Gestion_des_donnees

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

    with TaskGroup("Etage_du_scraping",) as group_scraping:
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
    
    with TaskGroup("Alimentation_des_bases_de_données",) as Ingection_BD:
        
    ###----------------------- Alimentationd de Mysql -----------------#####
        
        
        def mysql_Inge():
            doc = "/opt/airflow/Dossiers_json_excel_csv"
            gestion = Gestion_des_donnees(doc)
            return gestion.Mysql_ingection()

        python_Mysql_Ingection = PythonOperator(
            task_id="Mysql_Ingection",
            python_callable=mysql_Inge,

        )

    ###----------------------- Alimentationd de Postgres -----------------#####
        def Postgres_Inge():
            doc = "/opt/airflow/Dossiers_json_excel_csv"
            gestion = Gestion_des_donnees(doc)
            gestion.Postgres_ingection()           

        Python_Postgres_Ingection = PythonOperator(
            task_id="Postgres_Ingection",
            python_callable=Postgres_Inge,
          
        )
    ###------------------- Alimentation Mongo ------------------------####
        def MongoIng():
            doc = "/opt/airflow/Dossiers_json_excel_csv"
            gestion = Gestion_des_donnees(doc)
            gestion.creer_collection()           

        Python_mongo_ingection = PythonOperator(
            task_id="mongo_ingection",
            python_callable=MongoIng,

        )

    end_etape = BashOperator(
        task_id ='end', 
        bash_command = "echo fin - love and peace"
    )


    start_etape >> group_scraping >> Ingection_BD >> end_etape
    