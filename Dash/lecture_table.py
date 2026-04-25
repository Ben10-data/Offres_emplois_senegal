# eda_pandas.py
import pandas as pd
import psycopg2


def lecture(table):
    conn = psycopg2.connect(
    host="postgres_warehouse",
    port=5432,
    database="datawarehouse",
    user="admin",
    password="admin_pwd"
)
    query = f"SELECT * FROM {table}"

    df = pd.read_sql_query(query, conn)
    return df 

