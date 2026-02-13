#TODO: This file contains endpoints which MUST be removed before releasing, as they can e.g. wipe the entire database

from dotenv import load_dotenv
from app import app, get_db_connection

load_dotenv()



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