from utils_BD import ConnexionDB
import pandas as pd 
import os 
from pyspark.sql import SparkSession
from datetime import datetime

class ConnexionLake(ConnexionDB):

    def __init__(self):
        super().__init__()
    

#------- lecture des tables mysql et postgres (base de données SQL)-------------#
    

    #--------------- Mysql --------------------# 
    def voir_listes_tablesMysql(self):
        db_name = os.getenv("Mysql_DB")
        tables = pd.read_sql("show tables", self.get_mysql_conn())
        listes_tables = list(tables[f'Tables_in_{db_name}'].values)
        return listes_tables
    
    # --------------- PostgresQL -------------# 
    def voirlistes_tablesPostgres(self):
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        tables = pd.read_sql(query, self.get_postCon())
        return tables["table_name"].tolist()
    
    # -------------- Lecture de mongoDB ---------------------------# 
    def voir_listes_collections(self):
        tables = self.get_mongoCon().list_collection_names()
        return tables
    

#--------------- Inngection a hdfs ---------------------------- # 
    

    #----- pour -------- mysql_to_hdfs ---------------#

    def mysql_to_hdfs(self):

        for el in self.voir_listes_tablesMysql():

            # lectures de de chaque tables 
            query = f"SELECT * FROM {el}"
            df_mysql = pd.read_sql(query, self.get_mysql_conn())

            # Creation d'une session avec le connecteur de pySpark 
            spark = SparkSession.builder \
                .appName("MySQLtoHDFS") \
                .getOrCreate()
            
            # Conversion des bases mysql en dataframes spark et inject --> hdfs 
            df_spark = spark.createDataFrame(df_mysql)
            df_spark.write.mode("overwrite").parquet("hdfs://namenode:8020/ben/dataLake")
            
        return f'Datalake bien alimenté a partir de mysql a {datetime.now().ctime()}'
    

# ------ Ingectionn postgres_hdfs___--------------------### 
    
    def post_to_hdfs(self):

        for el in self.voirlistes_tablesPostgres():

            query = f"SELECT * FROM {el}"
            df_postgres = pd.read_sql(query, self.get_postCon())

            spark = SparkSession.builder \
                .appName("MySQLtoHDFS") \
                .getOrCreate()
            
            df_spark = spark.createDataFrame(df_postgres)
            df_spark.write.mode("overwrite").parquet("hdfs://namenode:8020/ben/dataLake")
        
        return f'Datalake bien alimenté a partir de Postgres a {datetime.now().ctime()}'


## ---_________-------- Ingection depuis mongoDB----------------------###
    
    def mongo_to_hdfs(self):

        for col in self.voir_listes_collections():
           
           # travailler avec chaque collection apres a partir de son nom 
           # on doit creer un object a partir du nom 
           col = self.get_mongoCon()[col] 
           docs = list(col.find({},{'_id':0}))

           df_mongo = pd.DataFrame(docs)

           spark = SparkSession.builder \
                .appName("MySQLtoHDFS") \
                .getOrCreate()
            
           df_spark = spark.createDataFrame(df_mongo)
           df_spark.write.mode("overwrite").parquet("hdfs://namenode:8020/ben/dataLake")
        
        return f'Datalake bien alimenté a partir de MongoDB a {datetime.now().ctime()}'


        


        




    
    
    

    










    
