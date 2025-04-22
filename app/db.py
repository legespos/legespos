import psycopg2
import os

_conn = None  # privado

def init_db():
    global _conn
    if _conn is None:
        _conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

def get_db_connection():
    if _conn is None:
        raise Exception("La conexión a la base de datos no está inicializada.")
    return _conn
