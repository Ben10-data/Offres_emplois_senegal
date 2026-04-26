# eda_pandas.py
import pandas as pd
import psycopg2


def lecture(table):
    conn = psycopg2.connect(
    host="dpg-d7n2vd1kh4rs73b028eg-a",
    port=5432,
    database="offres_emploi_postgres_id4c",
    user="offres_emploi_postgres_id4c_user",
    password="b3HTXg7CxbbMRfeafdVxeJxNJSPa3tkv",
)
    query = f"SELECT * FROM {table}"

    df = pd.read_sql_query(query, conn)
    return df 

