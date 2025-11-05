from pyspark.sql import SparkSession
from pyspark.sql.functions import col 


# creation d'une session spark 
spark = SparkSession.builder.appName("TestApp").getOrCreate()

# version de la version de spark 
spark.version

# lecture de nos fichier hdfs 
df = spark.read.parquet("hdfs://namenode:8020/ben/dataLake/")

# compter les nombres de lignes qu'on a 
df.count()

# voir le schema ou les differents colonnes de nos données 
df.printSchema()

# >>> df.printSchema()
# root
#  |-- entreprise: string (nullable = true)
#  |-- poste: string (nullable = true)
#  |-- niveau_etude: string (nullable = true)
#  |-- niveau_experience: string (nullable = true)
#  |-- contrat_propose: string (nullable = true)
#  |-- region: string (nullable = true)
#  |-- Competence: string (nullable = true)
#  |-- date_de_publication: string (nullable = true)
#  |-- formation: string (nullable = true)


#----------------- *** Colonnes a nettoyer et organiser ***-----------------------#
# Apres un passage de select, exemple la colonne suivant '"entreprise"
df.select("entreprise").distinct().show(5, truncate=False)

###---------------µ*******************************************----------------###

####     niveau_etude , niveau_experience, contrat_propose
####     region, Competence, formation



# Voir colonne par colonne, combien de fois une variable est répéter 
# pour les postes "poste"
df.groupby("poste").count().orderBy(col("count").desc()).show(10)

df.groupBy("entreprise").count().orderBy(col('count').desc()).show(10)


spark.stop()