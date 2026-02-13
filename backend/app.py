import time
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


from flask import Flask, send_from_directory, request

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

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/init_db')
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            sum_tournament_points INTEGER DEFAULT 0,
            sum_play_points INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS match_results (
            id SERIAL PRIMARY KEY,
            table_name CHAR NOT NULL,
            player_id INTEGER REFERENCES players(id),
            play_points INTEGER DEFAULT 0,
            tournament_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database initialized!\n"

@app.route('/match_view')
def match_view():
    return send_from_directory('../frontend', 'partietabelle.html')

@app.route('/post_match_result', methods=['POST'])
def post_match_result():
    try:
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {
        #     "table_name": "A",
        #     "player_id": 1,
        #     "play_points": 5,
        #     "tournament_points": 10
        # }

        for result in data:
            table_name = result.get('table_name')
            player_id = result.get('player_id')
            play_points = result.get('play_points')
            tournament_points = result.get('tournament_points')
            conn = get_db_connection()
            cur = conn.cursor()
            #TODO: We need real player_ids in the frontend to make this work
            #cur.execute('''
            #    INSERT INTO match_results (table_name, player_id, play_points, tournament_points)
            #    VALUES (%s, %s, %s, %s);
            #''', (table_name, player_id, play_points, tournament_points))
            conn.commit()
            cur.close()
            conn.close()
        return "Match result posted!\n"
    except Exception as e:
        return f"Error: {str(e)}\n", 400


####################################
###### DATABASE MANAGEMENT #########
####################################

#TODO: IMPORTANT: these endpoints need to be removed or portected before production;

@app.route('/dump_db')
def dump_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM players;')
    players = cur.fetchall()
    cur.execute('SELECT * FROM match_results;')
    match_results = cur.fetchall()
    cur.close()
    conn.close()
    
    response = "Players:\n"
    for player in players:
        response += f"{player}\n"
    
    response += "\nMatch Results:\n"
    for match_result in match_results:
        response += f"{match_result}\n"
    
    return response



@app.route('/populate_db_examples')
def populate_db_examples():
    conn = get_db_connection()
    cur = conn.cursor()

    # Insert players only when players table is empty
    cur.execute("""
        INSERT INTO players (username, sum_tournament_points, sum_play_points)
        SELECT v.username, v.sum_tournament_points, v.sum_play_points
        FROM (VALUES
            ('Alice', 10, 20),
            ('Bob', 15, 25),
            ('Charlie', 5, 10)
        ) AS v(username, sum_tournament_points, sum_play_points)
        WHERE NOT EXISTS (SELECT 1 FROM players)
    """)

    # Insert match_results only when match_results is empty;
    cur.execute("""
        INSERT INTO match_results (table_name, player_id, play_points, tournament_points)
        SELECT v.table_name, p.id, v.play_points, v.tournament_points
        FROM (VALUES
            ('A','Alice',5,10),
            ('B','Bob',10,15),
            ('C','Charlie',2,5)
        ) AS v(table_name, username, play_points, tournament_points)
        JOIN players p ON p.username = v.username
        WHERE NOT EXISTS (SELECT 1 FROM match_results)
    """)

    conn.commit()
    cur.close()
    conn.close()
    return "Example data ensured (inserted when tables were empty).\n"

@app.route('/reset_db')
def reset_db():
    # Reset the database (delete all data)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM match_results;')
    cur.execute('DELETE FROM players;')
    conn.commit()
    cur.close()
    conn.close()
    return "Database reset!\n"