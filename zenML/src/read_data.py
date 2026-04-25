import pandas as pd
import psycopg2
from zenml.steps import step 

@step
def read_data(query: str, table_name: str, host: str, port: int, database: str, user: str, password: str) -> pd.DataFrame:
    conn_params = {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "password": password
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        print("Connexion réussie à la base de données PostgreSQL")
        
       
        if not table_name.replace("_", "").isalnum():
            print("Nom de table invalide.")
            return pd.DataFrame()
        
        df = pd.read_sql_query(query, conn)
        print(f"{len(df)} lignes récupérées depuis '{table_name}'")
        return df
    except Exception as e:
        print(f"Erreur de connexion ou de requête : {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Connexion fermée.")



    