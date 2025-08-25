import os
import pandas as pd 
from sqlalchemy import create_engine
from pymongo import MongoClient
import datetime

from dotenv import load_dotenv
load_dotenv()

#---------------- La classe pour assurer les connexion au base de données--------#
class ConnexionDB:

    def __init__(self):
        self._mysql_connection = None 
        self._postgres_connection = None
        self._mongo_connection = None 
        self._client_airflow = None 

    

    #-------------- connection Mysql -----------------------#
    def get_mysql_conn(self):
        if self._mysql_connection is None:
            user="root"
            host = "mysql"
            password = os.getenv('Mysql_root_pwd')
            port = 3306
            db = os.getenv('Mysql_DB')
            self._mysql_connection = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}")

        return self._mysql_connection
    
    #-------------- connection Postgres -----------------------#
    def get_postCon(self):
        if self._postgres_connection is None : 
            user = os.getenv('Post_user')
            host = "postgresMetier"
            password=os.getenv('Post_pwd')
            port = 5432
            db= os.getenv('Post_DB')
            self._postgres_connection = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
    
        return self._postgres_connection
    
    #-------------- connection MongoDB -----------------------#
    def get_mongoCon(self, nom_de_la_base="Donnees_JOB"):
        if self._mongo_connection is None: 
            user_mongo = os.getenv('Mongo_user')
            password = os.getenv('Mongo_pwd')
            host = "mongodb"
            port = 27017
            uri = f"mongodb://{user_mongo}:{password}@{host}:{port}/?authSource=admin"
            client = MongoClient(uri)
            self._mongo_connection = client[nom_de_la_base]
        return self._mongo_connection
    
    

   

#-------------------- Ingection au bases de donnéees-----------------#

class Gestion_des_donnees(ConnexionDB):

    def __init__(self, dossiers_sources):
        super().__init__()
        self.dossiers = dossiers_sources
        self.date = datetime.date.today()
        

#------------------ Lecture des fichiers -----------------------------#
    
    def liens_des_fichiers(self):

        listes_des_fichiers = []
        for root, dirs, files in os.walk(self.dossiers):
            for file in files:
                if file.endswith('.csv') or file.endswith('.xls' or '.xlsx') or file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    listes_des_fichiers.append(full_path)
        return listes_des_fichiers
    
    def extrait_nom(self, chemin_fichier):
        nom_table = os.path.basename(chemin_fichier).split(".")[0]
        return nom_table
    
    ###------------ INgection sur Postgres--------------------####
    def Postgres_ingection(self):
        fichiers = self.liens_des_fichiers()
        for el in fichiers:
            nom_du_table = self.extrait_nom(el)
            if el.endswith('.csv'):
                pd_csv = pd.read_csv(el)
                pd_csv.to_sql(
                  name= f"{nom_du_table}_{self.date}".replace('-','_'), 
                  con= self.get_postCon(),          
                  if_exists="replace",       
                  index=False                
                )
            elif el.endswith('.xls'or '.xlsx'):
                pd_excel = pd.read_excel(el)
                pd_excel.to_sql(
                    name=f"{nom_du_table}_{self.date}".replace('-','_'),
                    con= self.get_postCon(),
                    if_exists="replace",
                    index=False
                )

            elif el.endswith('.json'):
                pd_json = pd.read_json(el)
                pd_json.to_sql(
                    name=f"{nom_du_table}_{self.date}".replace('-','_'),
                    con= self.get_postCon(),
                    if_exists="replace",
                    index=False
                )


    ### --------------------ingection mysql------------------------------####

    def Mysql_ingection(self):
        fichiers = self.liens_des_fichiers()
        for el in fichiers:
            nom_du_table = self.extrait_nom(el)
            if el.endswith('.csv'):
                pd_csv = pd.read_csv(el)
                pd_csv.to_sql(
                  name= f"{nom_du_table}_{self.date}".replace('-','_'),   
                  con= self.get_mysql_conn(),          
                  if_exists="replace",       
                  index=False                
                )
            elif el.endswith('.xls'or '.xlsx'):
                pd_excel = pd.read_excel(el)
                pd_excel.to_sql(
                    name=f"{nom_du_table}_{self.date}".replace('-','_'),
                    con= self.get_mysql_conn(),
                    if_exists="replace",
                    index=False
                )
            elif el.endswith('.json'):
                pd_json = pd.read_json(el)
                pd_json.to_sql(
                    name=f"{nom_du_table}_{self.date}".replace('-','_'),
                    con= self.get_mysql_conn(),
                    if_exists="replace",
                    index=False
                )

### -------------------Injection MongoDB----------------------------- ####

    def creer_collection(self):
        fichiers = self.liens_des_fichiers()
        for el in fichiers:
            nom_de_la_collection = self.extrait_nom(el) # chaque fichier est une collection
            collection = self.get_mongoCon()[f"{nom_de_la_collection}_{self.date}".replace('-','_')]
            # stockage des fichier csv 
            if el.endswith('.csv'):
                pd_csv = pd.read_csv(el)
                donnees = pd_csv.to_dict(orient='records')
                collection.insert_many(donnees)
            # stockage des fichiers excel 
            elif el.endswith('.xls'or '.xlsx'):
                pd_excel = pd.read_excel(el)
                donnees = pd_excel.to_dict(orient='records')
                collection.insert_many(donnees)
            # Stockage des fichiers json 
            elif el.endswith('.json'):
                pd_json = pd.read_json(el)            
                donnees = pd_json.to_dict(orient='records')
                collection.insert_many(donnees)
