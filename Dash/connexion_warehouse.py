import pandas as pd
import psycopg2

class Visualisation:
    def __init__(self, host, port, database, user, password):
        self.conn_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            print("Connexion réussie à la base de données PostgreSQL")
        except Exception as e:
            print(f" Erreur de connexion : {e}")
            self.conn = None

    def get_data(self, table_name):
        if not self.conn:
            print("Aucune connexion active.")
            return None
        
        # Sécurité basique contre l'injection SQL sur le nom de table
        if not table_name.replace("_", "").isalnum():
            print(" Nom de table invalide.")
            return None
            
        try:
            query = f'SELECT * FROM "{table_name}"'
            df = pd.read_sql_query(query, self.conn)
            print(f" {len(df)} lignes récupérées depuis '{table_name}'")
            return df
        except Exception as e:
            print(f" Erreur lors de la requête : {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()
            print("Connexion fermée.")