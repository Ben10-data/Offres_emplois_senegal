from airflow import DAG
from airflow.operators.bash import BashOperator 
from airflow.operators.python import PythonOperator

from airflow.decorators import task
from airflow.utils.task_group import TaskGroup
from datetime import datetime

from utils_BD import Gestion_des_donnees
from Utils_Data_Lake import ConnexionLake

with DAG(dag_id="Premier_dag", 
    start_date=datetime(2025,7,28), 
    schedule_interval=None,catchup=False, 
    description="Automatisation " \
    "d\' un pipeline ") as dag:
    
    # initialisation de notre dag 
    start_etape = BashOperator(
        task_id ="premier_Etape",
        bash_command = "echo Pipeline de cette semaine -offre a tenter sa chance dans la semaine"
    )

    # with TaskGroup("Etape_du_scrping",) as group_scraping:
    #     # On cree deux taches qui s'executer automatiquement 

    #     # Premiere tache de la semaine 
    #     tache1 = BashOperator(
    #         task_id = "scrap_emploi_dakar",
    #         bash_command = "cd /opt/airflow/scrapjob/scrapjob/spiders && scrapy crawl emploi_dakar"
    #     )
    #     # Deuxieme tache de la meme semaine 
    #     tache2 = BashOperator(
    #         task_id = "scrap_emploi_senegal", 
    #         bash_command = "cd /opt/airflow/scrapjob/scrapjob/spiders && scrapy crawl emploisenegal",
    #     )
    
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

    #------------Groupe des dataLake----------------------------------------###

    with TaskGroup('Alimentation_des_dataLake',) as group_Lake:
        
        alimentation_duLake = ConnexionLake()

        def inject_Lake():
            alimentation_duLake.post_to_hdfs()
            alimentation_duLake.mongo_to_hdfs()
            alimentation_duLake.mysql_to_hdfs()

        Python_mongo_ingection = PythonOperator(
            task_id="Injection_a_partir_mongo_post_mysql",
            python_callable=inject_Lake

        )





    

    end_etape = BashOperator(
        task_id ='a_suivre', 
        bash_command = "echo fin - love and peace"
    )


       
    #group_scraping >>

    start_etape >> Ingection_BD >> group_Lake >> end_etape 
    