import os
import logging
import psycopg2
from dotenv import load_dotenv

# --- Load env variables ---
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

CREATE_TABLES_PATH  = "postgreSQL/create_tables.sql"

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def connect_to_db():
    # --- Create global connection ---
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = False
        logging.info("Connected to PostgreSQL database successfully.")
        return conn
    except Exception as e:
        logging.error("Database connection failed", exc_info=True)
        raise

