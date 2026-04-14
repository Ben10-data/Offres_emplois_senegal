#### -------------------------------------------- Notre script Spark ---------------------------------#####

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, explode, regexp_replace,  date_format,  when, udf, to_date
from pyspark.sql import functions as F 
from pyspark.sql.types import DateType
from datetime import datetime


try:
   spark.stop()
except:
     pass 


# creation d'une session spark 
# #spark = SparkSession.builder \
#    .appName("Traitement_depuis_hdfs") \
#    .master("yarn") \
#    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
#    .config("spark.hadoop.yarn.resourcemanager.hostname", "resourcemanager") \
#    .getOrCreate()

spark = SparkSession.builder\
        .appName('traitement_NLP').getOrCreate()

# version de la version de spark 
spark.version


# lecture de nos fichier hdfs 
df = spark.read.option("mergeSchema", "true").parquet("hdfs://namenode:8020/ben/dataLake/")
df.count()


df = df.dropDuplicates()
# compter les nombres de lignes qu'on a 
df.count()


# voir le schema ou les differents colonnes de nos données 
df.printSchema()

# Les nombres de differents poste et  entreprises existantes 
df.select("poste").distinct().count()


df.select("entreprise").distinct().count()

#----------------- *** Colonnes a nettoyer et organiser ***-----------------------#
# Apres un passage de select, exemple la colonne suivant '"entreprise"
df.select("entreprise").distinct().show(5, truncate=False)

###------------- traitement de chaque colonne -------------------------------- ###### 

# ---------------- pour la colonne formation 

df_formation = df.withColumn(
    "formation_clean",
    F.trim(
        F.regexp_replace(F.col("formation"), r"</li><li>", ", "))
)

df_formation = df_formation.withColumn(
    "formation_clean",
    F.regexp_replace(F.col("formation_clean"), r"</?li>", "")
)

df_formation = df_formation.withColumn(
    "formation_clean",
    F.regexp_replace(F.col("formation_clean"), r"[\n]", "")
)

df_formation = df_formation.withColumn(
    "formation_clean",
    F.regexp_replace(F.col("formation_clean"),r"</?strong>", "")
)

df_formation = df_formation.withColumn(
    "formation_clean",
    F.trim(F.regexp_replace(F.col("formation_clean"), r"<[^>]+>", ""))
)

df_formation.drop("formation")



#-------------- Pour la colonne niveau_etude--------------

df_etude = df_formation.withColumn(
    "niveau_etude_clean",
    split(col("niveau_etude"), r"\s*(?:,|&|et)\s*")
)

df_etude = df_etude.drop("niveau_etude")
df_etude = df_etude.drop("formation")


##------------ contract proposé ---------------------------
df_contract = df_etude.withColumn(
    "contract",
    split(col("contrat_propose"), r"\s*(?:,|&|et)\s*")
)

df_contract = df_contract.drop("contrat_propose")


### ------------- Pour la region 

df_region = df_contract.withColumn(
    "region_clean",
    F.trim(F.regexp_replace(F.col("region"), r"\s*(?:\n|\t)", ""))

)

df_region = df_region.drop("region")



# ----- experience 

df_experience = df_region.withColumn(
    "experience", 
    split(col("niveau_experience"), r"\s*(?:,|&|-)\s*")
)

df_experience = df_experience.drop("niveau_experience")


#---------- Traitement des competences 

df_competence = df_experience.withColumn(
    "competences",
    split(col("Competence"), r"\s*(-)\s*")
)

df_date_nettoyer = df_competence.withColumn(
    "date_convertie",
    regexp_replace(col("date_de_publication"), "Publié le ", "")
)



# Fonction pour convertir les deux formats des dates 
def parse_date(date_str):
    if date_str is None:
        return None
    try:
        # Format 1: "12.06.2025"
        if "." in date_str and len(date_str.split(".")) == 3:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        
        # Format 2: "6 avril 2026"
        else:
            mois_fr_to_en = {
                'janvier': 'January', 'février': 'February', 'mars': 'March',
                'avril': 'April', 'mai': 'May', 'juin': 'June',
                'juillet': 'July', 'août': 'August', 'septembre': 'September',
                'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
            }
            parts = date_str.split()
            if len(parts) >= 3:
                jour = parts[0].zfill(2)
                mois_fr = parts[1]
                annee = parts[2]
                mois_en = mois_fr_to_en.get(mois_fr, mois_fr)
                return datetime.strptime(f"{jour} {mois_en} {annee}", "%d %B %Y").date()
    except:
        return None
    return None

# Appliquer la conversion
parse_date_udf = udf(parse_date, DateType())
df_date_formatee = df_date_nettoyer.withColumn(
    "date_typee", 
    parse_date_udf(col("date_convertie"))
)


# Vérifier
df_date_formatee.select("date_de_publication","date_convertie", "date_typee").show(10, truncate=False)

###---------------------------------------------------------------------------------#######""
#------------------------------------------------------------------------------------#
# Creation de la premiere dataset qui contient toutes les données 

df_clean = df_date_formatee.drop("Competence")
df_clean = df_clean.drop("date_convertie","date_de_publication")


df_clean.show(5, truncate=False)


#### ---------------- Creation du dataSet normale -------------------------###


##########___-------Mise en forme----------__________________________###
df_propres = df_clean.select("entreprise", "poste", col("competences").alias("competence"),
col("formation_clean").alias("formation"), col("niveau_etude_clean").alias("niveau_etude"),
col("contract").alias("contrat"), col("experience").alias("experience"),
col("region_clean").alias("region"), col("date_typee").alias("date_de_publication")
)


# Creation du deuxieme dataset pour le machine learning

df_ml = df_clean.select("entreprise", "poste", explode(col("competences")).alias("competence"),
col("formation_clean").alias("formation"), explode(col("niveau_etude_clean")).alias("niveau_etude"),
explode(col("contract")).alias("contrat"), explode(col("experience")).alias("experience"),
col("region_clean").alias("region"), col("date_typee").alias("date_de_publication")
)


print("dataset pour le machine learning et l'analyse analytique")
df_ml.show(10, truncate=False)




############----------------===============---------------------------===-----#######
### ---------------------- nos liens --------------------------------------------####
url = "jdbc:postgresql://postgres_warehouse:5432/datawarehouse"
user = "admin"
password = "admin_pwd"
driver = "org.postgresql.Driver"



df_propres.write\
    .format("jdbc")\
    .option("url", url)\
    .option("dbtable","offres_emploi")\
    .option("user", user)\
    .option("password",password)\
    .option("driver", driver)\
    .mode("append")\
    .save()


###---------------Creation du dataset ML --------------------------------####

df_ml.write\
    .format("jdbc")\
    .option("url", url)\
    .option("dbtable","offres_emploi_ml")\
    .option("user", user)\
    .option("password",password)\
    .option("driver", driver)\
    .mode("append")\
    .save()



print("--------------------------tout esst carree-----------------------------")


spark.stop()

del spark
print('la session spark est arretée et supprimée')