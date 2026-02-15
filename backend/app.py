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

@app.route("/match_view")
def serve_match_view():
    return send_from_directory('../frontend', 'partietabelle.html')

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/create_player', methods=['POST'])
def create_player():
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            return "Error: 'username' is required.\n", 400
        
        execute_query('INSERT INTO players (username) VALUES (%s);', (username,))
        return "Player created!\n"

    except Exception as e:
        return f"Error: {str(e)}\n", 400

@app.route('/get_players', methods=['GET'])
def get_players():
    result = execute_query('SELECT id, username, total_tournament_points, total_play_points FROM players;')
    
    players_list = []
    for player in result:
        players_list.append({
            'id': player[0],
            'username': player[1],
            'sum_tournament_points': player[2],
            'sum_play_points': player[3]
        })
    return {'players': players_list}

@app.route('/get_player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    result = execute_query('SELECT id, username, total_tournament_points, total_play_points FROM players WHERE id = %s;', (player_id,))
    if not result:
        return "Player not found.\n", 404
    player = result[0]
    return {
        'id': player[0],
        'username': player[1],
        'sum_tournament_points': player[2],
        'sum_play_points': player[3]
    }

@app.route('/get_players_by_table/<string:table_name>', methods=['GET'])
def get_players_by_table(table_name):
    result = execute_query('''
        SELECT p.id, p.username, p.total_tournament_points, p.total_play_points
        FROM players p
        JOIN tables t ON p.current_table_id = t.id
        WHERE t.table_name = %s;
    ''', (table_name,))
    
    players_list = []
    for player in result:
        players_list.append({
            'id': player[0],
            'username': player[1],
            'sum_tournament_points': player[2],
            'sum_play_points': player[3]
        })
    return {'players': players_list}

@app.route('/update_player_status', methods=['POST'])
def update_player_status():
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        new_status = data.get('is_active')
        current_table = data.get('current_table')
        if not player_id or new_status is None:
            return "Error: 'player_id' and 'is_active' are required.\n", 400
        
        execute_query('''
            UPDATE players SET is_active = %s, current_table_id = (SELECT id FROM tables WHERE table_name = %s) WHERE id = %s; ''', (new_status, current_table, player_id))
        return "Player status updated!\n"
    except Exception as e:
        return f"Error: {str(e)}\n", 400
    

@app.route('/post_match_result', methods=['POST'])
def post_match_result():
    try:
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}

        for result in data:
            table_name = result.get('table_name')
            player_id = result.get('player_id')
            play_points = result.get('play_points')
            tournament_points = result.get('tournament_points')

            execute_query('''
                UPDATE match_results
                SET total_play_points = %s, tournament_points = %s
                WHERE match_id = (SELECT id FROM matches WHERE table_id = (SELECT id FROM tables WHERE table_name = %s))
                AND player_id = %s;
            ''', (play_points, tournament_points, table_name, player_id))

        return "Match results updated!\n"
    except Exception as e:
        return f"Error: {str(e)}\n", 400
    
@app.route('/get_table/<string:table_name>', methods=['GET'])
def get_table(table_name):
    result = execute_query('SELECT id, table_name FROM tables WHERE table_name = %s;', (table_name,))
    if not result:
        return "Table not found.\n", 404
    table = result[0]
    return {
        'id': table[0],
        'table_name': table[1]
    }

@app.route('/get_tables', methods=['GET'])
def get_tables():
    result = execute_query('SELECT id, table_name FROM tables;')
    
    tables_list = []
    for table in result:
        tables_list.append({
            'id': table[0],
            'table_name': table[1]
        })
    return {'tables': tables_list}


@app.route('/init_db', methods=['GET'])
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id SERIAL PRIMARY KEY,
            table_name TEXT NOT NULL UNIQUE,
            is_occupied BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT FALSE,
            total_tournament_points INTEGER DEFAULT 0,
            total_play_points INTEGER DEFAULT 0,
            current_table_id INTEGER REFERENCES tables(id),
            current_match_id INTEGER REFERENCES matches(id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            table_id INTEGER NOT NULL REFERENCES tables(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            finished BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS rounds (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            round_number INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(match_id, round_number)
        );

        CREATE TABLE IF NOT EXISTS round_results (
            id SERIAL PRIMARY KEY,
            round_id INTEGER NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            play_points INTEGER DEFAULT 0,
            UNIQUE(round_id, player_id)
        );

        CREATE TABLE IF NOT EXISTS match_results (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            total_play_points INTEGER DEFAULT 0,
            final_standing INTEGER NOT NULL,
            tournament_points INTEGER DEFAULT 0,
            UNIQUE(match_id, player_id)
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database initialized!\n"






####################################
###### DATABASE MANAGEMENT #########
####################################

#TODO: IMPORTANT: these endpoints need to be removed or portected before production;

@app.route('/dump_db', methods=['GET'])
def dump_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM players;')
    players = cur.fetchall()
    cur.execute('SELECT * FROM tables;')
    tables = cur.fetchall()
    cur.execute('SELECT * FROM matches;')
    matches = cur.fetchall()
    cur.execute('SELECT * FROM rounds;')
    rounds = cur.fetchall()
    cur.execute('SELECT * FROM round_results;')
    round_results = cur.fetchall()
    cur.execute('SELECT * FROM match_results;')
    match_results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    response = "Players:\n"
    for player in players:
        response += f"{player}\n"
    
    response += "\nTables:\n"
    for t in tables:
        response += f"{t}\n"

    response += "\nMatches:\n"
    for m in matches:
        response += f"{m}\n"

    response += "\nRounds:\n"
    for r in rounds:
        response += f"{r}\n"

    response += "\nRound Results:\n"
    for rr in round_results:
        response += f"{rr}\n"

    response += "\nMatch Results:\n"
    for mr in match_results:
        response += f"{mr}\n"
    
    return response



@app.route('/populate_db_examples', methods=['GET'])
def populate_db_examples():
    conn = get_db_connection()
    cur = conn.cursor()

    # Insert players only when players table is empty
    cur.execute("""
        INSERT INTO players (username, total_tournament_points, total_play_points)
        SELECT v.username, v.total_tournament_points, v.total_play_points
        FROM (VALUES
            ('Alice', 10, 120),
            ('Bob', 15, 135),
            ('Charlie', 5, 90)
        ) AS v(username, total_tournament_points, total_play_points)
        WHERE NOT EXISTS (SELECT 1 FROM players)
    """)
    
    # Insert tables when empty
    cur.execute("""
        INSERT INTO tables (table_name)
        SELECT v.table_name
        FROM (VALUES ('A'),('B'),('C')) AS v(table_name)
        WHERE NOT EXISTS (SELECT 1 FROM tables)
    """)

    # Insert matches only when matches is empty (one match per table)
    cur.execute("""
        INSERT INTO matches (table_id, finished)
        SELECT t.id, TRUE
        FROM tables t
        WHERE NOT EXISTS (SELECT 1 FROM matches)
        ORDER BY t.id
        LIMIT 3
    """)

    # Insert rounds for each match (3 rounds per match as example)
    cur.execute("""
        INSERT INTO rounds (match_id, round_number)
        SELECT m.id, v.round_number
        FROM matches m
        CROSS JOIN (VALUES (1), (2), (3)) AS v(round_number)
        WHERE NOT EXISTS (SELECT 1 FROM rounds)
    """)

    # Insert round_results
    cur.execute("""
        INSERT INTO round_results (round_id, player_id, play_points)
        SELECT r.id, p.id, 
            CASE 
                WHEN p.username = 'Alice' THEN 20 + (r.round_number * 10)
                WHEN p.username = 'Bob' THEN 25 + (r.round_number * 10)
                WHEN p.username = 'Charlie' THEN 15 + (r.round_number * 10)
            END
        FROM rounds r
        JOIN matches m ON r.match_id = m.id
        JOIN tables t ON m.table_id = t.id
        CROSS JOIN players p
        WHERE NOT EXISTS (SELECT 1 FROM round_results)
        AND (
            (t.table_name = 'A' AND p.username = 'Alice') OR
            (t.table_name = 'B' AND p.username = 'Bob') OR
            (t.table_name = 'C' AND p.username = 'Charlie')
        )
    """)

    # Insert match_results with final standings and tournament points
    cur.execute("""
        INSERT INTO match_results (match_id, player_id, total_play_points, final_standing, tournament_points)
        SELECT m.id, p.id, v.total_play_points, v.final_standing, v.tournament_points
        FROM (VALUES
            ('A','Alice', 60, 1, 10),
            ('B','Bob', 75, 1, 15),
            ('C','Charlie', 45, 2, 5)
        ) AS v(table_name, username, total_play_points, final_standing, tournament_points)
        JOIN tables t ON t.table_name = v.table_name
        JOIN matches m ON m.table_id = t.id
        JOIN players p ON p.username = v.username
        WHERE NOT EXISTS (SELECT 1 FROM match_results)
    """)

    conn.commit()
    cur.close()
    conn.close()
    return "Example data ensured (inserted when tables were empty).\n"

@app.route('/reset_db', methods=['GET'])
def reset_db():
    # Reset the database (delete all data)
    conn = get_db_connection()
    cur = conn.cursor()
    # delete child tables first to satisfy FK constraints
    cur.execute('DELETE FROM round_results;')
    cur.execute('DELETE FROM match_results;')
    cur.execute('DELETE FROM rounds;')
    cur.execute('DELETE FROM matches;')
    cur.execute('DELETE FROM tables;')
    cur.execute('DELETE FROM players;')
    conn.commit()
    cur.close()
    conn.close()
    return "Database reset!\n"


@app.route('/drop_db', methods=['GET'])
def drop_db():
    # Drop all tables (dangerous)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS round_results;')
    cur.execute('DROP TABLE IF EXISTS match_results;')
    cur.execute('DROP TABLE IF EXISTS rounds;')
    cur.execute('DROP TABLE IF EXISTS matches;')
    cur.execute('DROP TABLE IF EXISTS tables;')
    cur.execute('DROP TABLE IF EXISTS players;')
    conn.commit()
    cur.close()
    conn.close()
    return "Database dropped!\n"