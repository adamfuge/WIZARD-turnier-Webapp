import time
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


from flask import Flask

app = Flask(__name__)

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

@app.route('/')
def hello():
    count = get_hit_count()
    return f'Hello World! I have been seen {count} times.\n'

#more for debugging, get current content of database
@app.route('/dump_db')
def dump_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM players;')
    players = cur.fetchall()
    cur.execute('SELECT * FROM tournaments;')
    tournaments = cur.fetchall()
    cur.close()
    conn.close()
    
    response = "Players:\n"
    for player in players:
        response += f"{player}\n"
    
    response += "\nTournaments:\n"
    for tournament in tournaments:
        response += f"{tournament}\n"
    
    return response

@app.route('/init_db')
def init_db():
    # Initialize the database (create tables, etc.)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            sum_tournament_points INTEGER DEFAULT 0,
            sum_play_points INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS tournaments (
            id SERIAL PRIMARY KEY,
            table_name CHAR NOT NULL,
            player_id INTEGER REFERENCES players(id),
            play_points INTEGER DEFAULT 0,
            tournament_points INTEGER DEFAULT 0

        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database initialized!\n"