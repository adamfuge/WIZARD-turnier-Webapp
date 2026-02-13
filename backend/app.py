import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from flask import Flask


app = Flask(__name__, static_folder='../frontend/static', static_url_path='/static')

def get_hit_count():
    return 5

def get_db_connection():
    # Connect to the PostgreSQL database using environment variables
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "wizard"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "pass")
    )
    return conn