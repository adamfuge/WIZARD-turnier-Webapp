import psycopg2
import os
import string
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

@app.route("/tournament_view")
def serve_tournament_view():
    return send_from_directory('../frontend', 'turniertabelle.html')

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall() 
    conn.commit()
    cur.close()
    conn.close()
    return data

@app.route("/tournament_data")
def tournament_data():
    try:

        result = execute_query('''
            WITH R as(
            SELECT RANK() OVER (ORDER BY sum(tournament_points) DESC, 
            							sum(mr.total_play_points) DESC,
                                        sum(mr.round_wins) DESC,
										max(mr.total_play_points) DESC,
										(select count(*) from match_results mr2 where p.id=mr2.player_id and mr2.total_play_points=max(mr.total_play_points)) DESC,
										(select max(mr2.total_play_points) from match_results mr2 where p.id=mr2.player_id and mr2.total_play_points<max(mr.total_play_points)) DESC
                                        )
            							AS standing, 
            		username, 
            		sum(tournament_points) TP, 
            		sum(mr.total_play_points) PP,
            		status,
					sum(mr.round_wins) as rounds_won,
					max(mr.total_play_points) as best,
					(select count(*) from match_results mr2 where p.id=mr2.player_id and mr2.total_play_points=max(mr.total_play_points)) as anzahl,
					(select max(mr2.total_play_points) from match_results mr2 where p.id=mr2.player_id and mr2.total_play_points<max(mr.total_play_points)) as secondbest
            FROM match_results mr
            JOIN matches m ON mr.match_id = m.id
            JOIN players p ON mr.player_id = p.id
            GROUP BY p.id, username)

            SELECT r1.standing, r1.username, r1.tp, r1.pp,rounds_won, best, anzahl, secondbest, 
            	CASE 
            		WHEN status = 'hat_bereits_qualifikation' THEN 'hat_bereits_qualifikation' 
            		WHEN status = 'disqualifiziert' THEN 'disqualifiziert'
            		WHEN r1.standing <= 12 + (select count(*) from R r2 where r2.standing < r1.standing and r2.status <> 'none') THEN 'qualifiziert'
            		ELSE 'none'
            	END as status2
            FROM R r1
            ;
            ''')
        
        if result is None:
            return {'tournament_data': [], 'message': 'No data found or database query failed.'}

        

        tournament_data = []
        for row in result:
            tournament_data.append({
                'rank': row[0],
                'spieler': row[1],
                'TP': row[2],
                'EP': row[3],
                'status': row[8]
            })

        return tournament_data
    
    
    except Exception as e:
        return f"Error: {str(e)}\n", 400


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
    
@app.route('/post_round_result', methods=['POST'])
def post_round_result():
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
        return f"Error serverside: {str(e)}\n", 400

@app.route('/post_match_start', methods=['POST'])
def post_match_start():
    try:
        data = request.get_json()
        # the match start is an object with the following structure:
        # {"vorrunde": 1, "table_name": "A", "player_ids": [5,99,7]}

        table_name = data.get('table_name')
        vorrunde_id = data.get('vorrunde')

        execute_query('''
            INSERT INTO matches (table_id, vorrunde_id)
            VALUES ((SELECT t.id FROM tables t WHERE table_name = %s),
            		(SELECT v.id FROM vorrunden v WHERE v.id = %s))
            RETURNING id
        ''', (table_name, vorrunde_id))

        return "Match ready to start!\n"
    except Exception as e:
        return f"Error serverside: {str(e)}\n", 400

@app.route('/post_match_result', methods=['POST'])
def post_match_result():
    try:
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}

        
        execute_query('''
            UPDATE matches 
            SET finished_at = CURRENT_TIMESTAMP, finished = true
            WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
            AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s)
            RETURNING id;''', (data[0].get('tisch'),data[0].get('vorrunde')))
            

        for result in data:
            table_name = result.get('tisch')
            vorrunde_id = result.get('vorrunde')
            player_id = result.get('spieler')
            play_points = result.get('partiepunkte')
            final_standing = result.get('platzierung')
            tournament_points = result.get('turnierpunkte')
            round_wins = result.get('plusrunden')

            execute_query('''
                
                INSERT INTO match_results (match_id, player_id, total_play_points, final_standing, tournament_points, round_wins)
                VALUES ((SELECT m.id
                			FROM matches m
                			JOIN tables t ON t.id = m.table_id 
                			JOIN vorrunden v ON v.id = m.vorrunde_id 
                			WHERE table_name = %s
                			AND vorrunde_id = %s),
                		%s,
                		%s,
                		%s,
                		%s,
                		%s)
                RETURNING id
            ''', (table_name, vorrunde_id, player_id, play_points, final_standing, tournament_points, round_wins))

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

@app.route('/get_table_names', methods=['GET'])
def get_table_names():
    result = execute_query('SELECT table_name FROM tables;')
    
    tables_list = []
    for table in result:
        tables_list.append(table[0])
    return tables_list


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

        CREATE TABLE IF NOT EXISTS vorrunden (
            id SERIAL PRIMARY KEY,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            vorrunde_id INTEGER NOT NULL REFERENCES vorrunden(id),
            table_id INTEGER NOT NULL REFERENCES tables(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            finished BOOLEAN DEFAULT FALSE,
            UNIQUE (table_id, vorrunde_id)
        );

        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT FALSE,
            total_tournament_points INTEGER DEFAULT 0,
            total_play_points INTEGER DEFAULT 0,
            current_table_id INTEGER REFERENCES tables(id),
            current_match_id INTEGER REFERENCES matches(id),
            status TEXT DEFAULT 'none'
        );

        CREATE TABLE IF NOT EXISTS rounds (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            round_number INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (match_id, round_number)
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
            round_wins INTEGER DEFAULT 0,
            final_standing INTEGER,
            tournament_points INTEGER DEFAULT 0,
            UNIQUE(match_id, player_id)
        );
                
        CREATE TABLE IF NOT EXISTS tiebreaker_results (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            final_standing INTEGER NOT NULL,
            UNIQUE(match_id, player_id)
        );

        CREATE TABLE IF NOT EXISTS tournamentpoints_from_rank (
            rank SERIAL PRIMARY KEY,
            tp INTEGER NOT NULL
        );
        INSERT INTO tournamentpoints_from_rank 
        SELECT * 
        FROM (VALUES (1,45),(2,30),(3,20),(4,10),(5,5))
        WHERE NOT EXISTS ( SELECT 1 FROM tournamentpoints_from_rank);

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


@app.route('/populate_db_last_year', methods=['GET'])
def populate_db_last_year():
    try:
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}
        
        
        # Insert vorrunden
        execute_query("""
            INSERT INTO vorrunden (id, start_time)
            SELECT v.id, to_timestamp(v.start_time, 'D.M.YYYY HH24:MI')
            FROM (VALUES (1, '1.1.2003 12:00'), 
            		(2, '1.1.2003 14:00'), 
            		(3, '1.1.2003 16:00'), 
            		(5, '1.1.2000 16:00')) as v(id, start_time)
            WHERE NOT EXISTS (SELECT 1 FROM vorrunden)
            RETURNING id;
        """)
        
        for letter in string.ascii_uppercase:
            execute_query("""
                INSERT INTO tables (table_name)
                SELECT v.table_name
                FROM (VALUES (%s)) AS v(table_name)
                WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = %s)
                RETURNING id;
            """, (letter,letter))

        
        data = [
                {"vorrunde": 1,'tisch':'A','spieler': 94,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'A','spieler': 46,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 1,'tisch':'A','spieler': 15,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'A','spieler': 36,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 1,'tisch':'B','spieler': 64,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'B','spieler': 90,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'B','spieler': 30,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 3},{"vorrunde": 1,'tisch':'B','spieler': 49,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'C','spieler': 77,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'C','spieler': 73,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'C','spieler': 10,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 1,'tisch':'C','spieler': 89,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'D','spieler': 31,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'D','spieler': 5,'turnierpunkte': 30,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'D','spieler': 67,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'D','spieler': 58,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 5},{"vorrunde": 1,'tisch':'E','spieler': 13,'turnierpunkte': 45,'partiepunkte': 210,'plusrunden': 4},{"vorrunde": 1,'tisch':'E','spieler': 40,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 3},{"vorrunde": 1,'tisch':'E','spieler': 50,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 4},{"vorrunde": 1,'tisch':'E','spieler': 8,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'F','spieler': 24,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 1,'tisch':'F','spieler': 51,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 6},{"vorrunde": 1,'tisch':'F','spieler': 14,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 1,'tisch':'F','spieler': 45,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 1,'tisch':'G','spieler': 21,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'G','spieler': 35,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 6},{"vorrunde": 1,'tisch':'G','spieler': 53,'turnierpunkte': 20,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'G','spieler': 2,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'H','spieler': 63,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 1,'tisch':'H','spieler': 6,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 7},{"vorrunde": 1,'tisch':'H','spieler': 102,'turnierpunkte': 45,'partiepunkte': 360,'plusrunden': 9},{"vorrunde": 1,'tisch':'H','spieler': 54,'turnierpunkte': 20,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'I','spieler': 92,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 1,'tisch':'I','spieler': 87,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'I','spieler': 84,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'I','spieler': 82,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 1,'tisch':'J','spieler': 75,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'J','spieler': 60,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 1,'tisch':'J','spieler': 97,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'J','spieler': 80,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 1,'tisch':'K','spieler': 72,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 5},{"vorrunde": 1,'tisch':'K','spieler': 16,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'K','spieler': 78,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'K','spieler': 42,'turnierpunkte': 45,'partiepunkte': 380,'plusrunden': 9},{"vorrunde": 1,'tisch':'L','spieler': 37,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 1,'tisch':'L','spieler': 4,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'L','spieler': 26,'turnierpunkte': 20,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'L','spieler': 52,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 10},{"vorrunde": 1,'tisch':'M','spieler': 11,'turnierpunkte': 30,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 1,'tisch':'M','spieler': 98,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 1,'tisch':'M','spieler': 17,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 1,'tisch':'M','spieler': 33,'turnierpunkte': 45,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 1,'tisch':'N','spieler': 68,'turnierpunkte': 45,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 1,'tisch':'N','spieler': 96,'turnierpunkte': 20,'partiepunkte': 50,'plusrunden': 3},{"vorrunde": 1,'tisch':'N','spieler': 12,'turnierpunkte': 30,'partiepunkte': 60,'plusrunden': 3},{"vorrunde": 1,'tisch':'N','spieler': 41,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 1,'tisch':'O','spieler': 101,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 8},{"vorrunde": 1,'tisch':'O','spieler': 32,'turnierpunkte': 20,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 1,'tisch':'O','spieler': 25,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 1,'tisch':'O','spieler': 18,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 19,'turnierpunkte': 10,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 47,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'P','spieler': 7,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 9,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'Q','spieler': 55,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'Q','spieler': 79,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'Q','spieler': 62,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'Q','spieler': 38,'turnierpunkte': 45,'partiepunkte': 420,'plusrunden': 9},{"vorrunde": 1,'tisch':'R','spieler': 81,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'R','spieler': 59,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'R','spieler': 43,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 1,'tisch':'R','spieler': 66,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'S','spieler': 22,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'S','spieler': 83,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'S','spieler': 93,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'S','spieler': 39,'turnierpunkte': 10,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'T','spieler': 1,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 7},{"vorrunde": 1,'tisch':'T','spieler': 27,'turnierpunkte': 10,'partiepunkte': -20,'plusrunden': 3},{"vorrunde": 1,'tisch':'T','spieler': 34,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'T','spieler': 57,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'U','spieler': 88,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 1,'tisch':'U','spieler': 76,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'U','spieler': 20,'turnierpunkte': 10,'partiepunkte': -10,'plusrunden': 4},{"vorrunde": 1,'tisch':'U','spieler': 100,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 1,'tisch':'V','spieler': 29,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'V','spieler': 48,'turnierpunkte': 20,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 1,'tisch':'V','spieler': 91,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 1,'tisch':'V','spieler': 23,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 1,'tisch':'W','spieler': 61,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 1,'tisch':'W','spieler': 65,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'W','spieler': 95,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'W','spieler': 71,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'X','spieler': 56,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'X','spieler': 3,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 1,'tisch':'X','spieler': 70,'turnierpunkte': 10,'partiepunkte': 40,'plusrunden': 4},{"vorrunde": 1,'tisch':'X','spieler': 99,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 1,'tisch':'Y','spieler': 44,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 1,'tisch':'Y','spieler': 86,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 7},{"vorrunde": 1,'tisch':'Y','spieler': 103,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 9},{"vorrunde": 1,'tisch':'Y','spieler': 28,'turnierpunkte': 10,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 74,'turnierpunkte': 10,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 69,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 104,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 1,'tisch':'Z','spieler': 85,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 8}
,
{"vorrunde": 2,'tisch':'A','spieler': 51,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'A','spieler': 81,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'A','spieler': 4,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 2,'tisch':'A','spieler': 94,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 2,'tisch':'B','spieler': 36,'turnierpunkte': 30,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 2,'tisch':'B','spieler': 53,'turnierpunkte': 45,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'B','spieler': 66,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'B','spieler': 37,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 2,'tisch':'C','spieler': 46,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'C','spieler': 2,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 2,'tisch':'C','spieler': 11,'turnierpunkte': 45,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'C','spieler': 43,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 2,'tisch':'D','spieler': 15,'turnierpunkte': 45,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 21,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 98,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 83,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'E','spieler': 17,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 5},{"vorrunde": 2,'tisch':'E','spieler': 93,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 2,'tisch':'E','spieler': 49,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 2,'tisch':'E','spieler': 35,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 2,'tisch':'F','spieler': 54,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'F','spieler': 33,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 2,'tisch':'F','spieler': 22,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'F','spieler': 64,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 2,'tisch':'G','spieler': 90,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'G','spieler': 63,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'G','spieler': 39,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 2,'tisch':'G','spieler': 96,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 2,'tisch':'H','spieler': 30,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 2,'tisch':'H','spieler': 68,'turnierpunkte': 10,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 2,'tisch':'H','spieler': 6,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 2,'tisch':'H','spieler': 70,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'I','spieler': 10,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'I','spieler': 41,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 5},{"vorrunde": 2,'tisch':'I','spieler': 57,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 7},{"vorrunde": 2,'tisch':'I','spieler': 102,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'J','spieler': 12,'turnierpunkte': 45,'partiepunkte': 390,'plusrunden': 9},{"vorrunde": 2,'tisch':'J','spieler': 89,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'J','spieler': 71,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 2,'tisch':'J','spieler': 92,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'K','spieler': 87,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 2,'tisch':'K','spieler': 25,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'K','spieler': 77,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 10},{"vorrunde": 2,'tisch':'K','spieler': 1,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'L','spieler': 84,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'L','spieler': 18,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'L','spieler': 76,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 2,'tisch':'L','spieler': 73,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 2,'tisch':'M','spieler': 5,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'M','spieler': 82,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'M','spieler': 101,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'M','spieler': 27,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 2,'tisch':'N','spieler': 67,'turnierpunkte': 45,'partiepunkte': 350,'plusrunden': 8},{"vorrunde": 2,'tisch':'N','spieler': 20,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'N','spieler': 60,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'N','spieler': 32,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 2,'tisch':'O','spieler': 58,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 2,'tisch':'O','spieler': 100,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'O','spieler': 75,'turnierpunkte': 45,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'O','spieler': 7,'turnierpunkte': 30,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'P','spieler': 80,'turnierpunkte': 30,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 2,'tisch':'P','spieler': 9,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 2,'tisch':'P','spieler': 3,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'P','spieler': 31,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 2,'tisch':'Q','spieler': 97,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 2,'tisch':'Q','spieler': 13,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 2,'tisch':'Q','spieler': 29,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'Q','spieler': 47,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 26,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 38,'turnierpunkte': 45,'partiepunkte': 160,'plusrunden': 6},{"vorrunde": 2,'tisch':'R','spieler': 56,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 24,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 2,'tisch':'S','spieler': 50,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 2,'tisch':'S','spieler': 42,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 2,'tisch':'S','spieler': 55,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 2,'tisch':'S','spieler': 48,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 2,'tisch':'T','spieler': 8,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 2,'tisch':'T','spieler': 72,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 2,'tisch':'T','spieler': 79,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 10},{"vorrunde": 2,'tisch':'T','spieler': 86,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 2,'tisch':'U','spieler': 16,'turnierpunkte': 30,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 2,'tisch':'U','spieler': 62,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 2,'tisch':'U','spieler': 65,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 10},{"vorrunde": 2,'tisch':'U','spieler': 14,'turnierpunkte': 20,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 2,'tisch':'V','spieler': 40,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'V','spieler': 78,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 2,'tisch':'V','spieler': 44,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 2,'tisch':'V','spieler': 91,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'W','spieler': 85,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'W','spieler': 45,'turnierpunkte': 45,'partiepunkte': 120,'plusrunden': 6},{"vorrunde": 2,'tisch':'W','spieler': 59,'turnierpunkte': 20,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 2,'tisch':'W','spieler': 95,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 2,'tisch':'X','spieler': 34,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 2,'tisch':'X','spieler': 88,'turnierpunkte': 30,'partiepunkte': 380,'plusrunden': 10},{"vorrunde": 2,'tisch':'X','spieler': 61,'turnierpunkte': 20,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'X','spieler': 74,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 9},{"vorrunde": 2,'tisch':'Y','spieler': 52,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 9},{"vorrunde": 2,'tisch':'Y','spieler': 19,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 2,'tisch':'Y','spieler': 69,'turnierpunkte': 20,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 2,'tisch':'Y','spieler': 103,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 2,'tisch':'Z','spieler': 28,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'Z','spieler': 99,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 2,'tisch':'Z','spieler': 23,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 2,'tisch':'Z','spieler': 104,'turnierpunkte': 45,'partiepunkte': 370,'plusrunden': 8}
,
{"vorrunde": 3,'tisch':'A','spieler': 49,'turnierpunkte': 45,'partiepunkte': 350,'plusrunden': 8},{"vorrunde": 3,'tisch':'A','spieler': 94,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 3,'tisch':'A','spieler': 5,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 4},{"vorrunde": 3,'tisch':'A','spieler': 10,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 7},{"vorrunde": 3,'tisch':'B','spieler': 14,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 3,'tisch':'B','spieler': 54,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'B','spieler': 13,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 6},{"vorrunde": 3,'tisch':'B','spieler': 53,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'C','spieler': 60,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 3,'tisch':'C','spieler': 26,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 5},{"vorrunde": 3,'tisch':'C','spieler': 92,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'C','spieler': 78,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 3,'tisch':'D','spieler': 96,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 3,'tisch':'D','spieler': 7,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 3,'tisch':'D','spieler': 11,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 3,'tisch':'D','spieler': 25,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'E','spieler': 59,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 3,'tisch':'E','spieler': 70,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 3,'tisch':'E','spieler': 83,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 3,'tisch':'E','spieler': 55,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 3,'tisch':'F','spieler': 48,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 3,'tisch':'F','spieler': 56,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'F','spieler': 85,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 3,'tisch':'F','spieler': 88,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 3,'tisch':'G','spieler': 89,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 3,'tisch':'G','spieler': 64,'turnierpunkte': 10,'partiepunkte': 40,'plusrunden': 3},{"vorrunde": 3,'tisch':'G','spieler': 40,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'G','spieler': 67,'turnierpunkte': 20,'partiepunkte': 70,'plusrunden': 3},{"vorrunde": 3,'tisch':'H','spieler': 2,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 3,'tisch':'H','spieler': 74,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'H','spieler': 87,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 3,'tisch':'H','spieler': 63,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 3,'tisch':'I','spieler': 42,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'I','spieler': 75,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 3,'tisch':'I','spieler': 52,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 3,'tisch':'I','spieler': 98,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 3,'tisch':'J','spieler': 18,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 3,'tisch':'J','spieler': 68,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'J','spieler': 9,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 3,'tisch':'J','spieler': 79,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 3,'tisch':'K','spieler': 93,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 5},{"vorrunde": 3,'tisch':'K','spieler': 69,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 7},{"vorrunde": 3,'tisch':'K','spieler': 81,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 3,'tisch':'K','spieler': 76,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 65,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 46,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 3,'tisch':'L','spieler': 90,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 3,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 3,'tisch':'M','spieler': 45,'turnierpunkte': 20,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'M','spieler': 77,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 7},{"vorrunde": 3,'tisch':'M','spieler': 58,'turnierpunkte': 10,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'M','spieler': 50,'turnierpunkte': 45,'partiepunkte': 390,'plusrunden': 8},{"vorrunde": 3,'tisch':'N','spieler': 6,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 3,'tisch':'N','spieler': 80,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 3,'tisch':'N','spieler': 21,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'N','spieler': 84,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'O','spieler': 4,'turnierpunkte': 45,'partiepunkte': 400,'plusrunden': 10},{"vorrunde": 3,'tisch':'O','spieler': 17,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 5},{"vorrunde": 3,'tisch':'O','spieler': 41,'turnierpunkte': 10,'partiepunkte': 160,'plusrunden': 4},{"vorrunde": 3,'tisch':'O','spieler': 72,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 3},{"vorrunde": 3,'tisch':'P','spieler': 47,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 3,'tisch':'P','spieler': 66,'turnierpunkte': 30,'partiepunkte': 310,'plusrunden': 7},{"vorrunde": 3,'tisch':'P','spieler': 62,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 3,'tisch':'P','spieler': 101,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 3,'tisch':'Q','spieler': 33,'turnierpunkte': 10,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 37,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 32,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 12,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'R','spieler': 73,'turnierpunkte': 20,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 3,'tisch':'R','spieler': 15,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'R','spieler': 30,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 5},{"vorrunde": 3,'tisch':'R','spieler': 61,'turnierpunkte': 0,'partiepunkte': 0,'plusrunden': 0},{"vorrunde": 3,'tisch':'S','spieler': 35,'turnierpunkte': 45,'partiepunkte': 340,'plusrunden': 8},{"vorrunde": 3,'tisch':'S','spieler': 8,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'S','spieler': 31,'turnierpunkte': 10,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'S','spieler': 51,'turnierpunkte': 20,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 3,'tisch':'T','spieler': 102,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'T','spieler': 97,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 3,'tisch':'T','spieler': 28,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 3,'tisch':'T','spieler': 16,'turnierpunkte': 10,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 3,'tisch':'U','spieler': 38,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'U','spieler': 43,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 7},{"vorrunde": 3,'tisch':'U','spieler': 19,'turnierpunkte': 45,'partiepunkte': 340,'plusrunden': 8},{"vorrunde": 3,'tisch':'U','spieler': 44,'turnierpunkte': 10,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'V','spieler': 71,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 3,'tisch':'V','spieler': 22,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'V','spieler': 91,'turnierpunkte': 20,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'V','spieler': 20,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 3,'tisch':'W','spieler': 86,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 5},{"vorrunde": 3,'tisch':'W','spieler': 29,'turnierpunkte': 20,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 3,'tisch':'W','spieler': 27,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 3,'tisch':'W','spieler': 99,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'X','spieler': 23,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 3,'tisch':'X','spieler': 1,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'X','spieler': 95,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 3,'tisch':'X','spieler': 100,'turnierpunkte': 0,'partiepunkte': 0,'plusrunden': 0},{"vorrunde": 3,'tisch':'Y','spieler': 82,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 3,'tisch':'Y','spieler': 39,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'Y','spieler': 103,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'Y','spieler': 34,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'Z','spieler': 104,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 5},{"vorrunde": 3,'tisch':'Z','spieler': 36,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'Z','spieler': 24,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'Z','spieler': 57,'turnierpunkte': 10,'partiepunkte': -190,'plusrunden': 4}


                ]
         
#
        for result in data:
            table_name = result.get('tisch')
            vorrunde_id = result.get('vorrunde')
            player_id = result.get('spieler')
            play_points = result.get('partiepunkte')
            final_standing = result.get('platzierung')
            tournament_points = result.get('turnierpunkte')
            round_wins = result.get('plusrunden')
#
            execute_query('''
                INSERT INTO players (id, username)
                SELECT * 
                FROM (VALUES (%s,%s))
                WHERE NOT EXISTS (SELECT 1 FROM players WHERE id = %s)
                RETURNING id;
            ''', (player_id, player_id, player_id))
#
            execute_query('''
                INSERT INTO matches (table_id, vorrunde_id)
                SELECT * 
                FROM (VALUES ((SELECT t.id FROM tables t WHERE table_name = %s),
							  (SELECT v.id FROM vorrunden v WHERE v.id = %s)))
                WHERE NOT EXISTS (SELECT 1 
									FROM matches 
									WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
            						AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s))
                RETURNING id;
            ''', (table_name, vorrunde_id, table_name, vorrunde_id))

            
            execute_query('''
                INSERT INTO match_results (match_id, player_id, total_play_points, final_standing, tournament_points, round_wins)
                VALUES ((SELECT m.id
                			FROM matches m
                			JOIN tables t ON t.id = m.table_id 
                			JOIN vorrunden v ON v.id = m.vorrunde_id 
                			WHERE table_name = %s
                			AND vorrunde_id = %s),
                		%s,
                		%s,
                		%s,
                		%s,
                		%s)
                RETURNING id
            ''', (table_name, vorrunde_id, player_id, play_points, final_standing, tournament_points, round_wins))

        return "Match results updated!\n"
    except Exception as e:
        return f"Error: {str(e)}\n", 400

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
            ('Charlie1', 5, 90),
            ('Charlie2', 5, 90),
            ('Charlie3', 5, 90),
            ('Charlie4', 5, 90),
            ('Charlie5', 5, 90),
            ('Charlie6', 5, 90),
            ('Charlie7', 5, 90)
        ) AS v(username, total_tournament_points, total_play_points)
        WHERE NOT EXISTS (SELECT 1 FROM players);
        update players
        set status = 'hat_bereits_qualifikation'
        where username = 'Charlie5';
        update players
        set status = 'disqualifiziert'
        where username = 'Charlie3';

    """)

    # Insert vorrunden
    cur.execute("""
        INSERT INTO vorrunden (id, start_time)
        SELECT v.id, to_timestamp(v.start_time, 'D.M.YYYY HH24:MI')
        FROM (VALUES (1, '1.1.2003 12:00'), 
        		(2, '1.1.2003 14:00'), 
        		(3, '1.1.2003 16:00'), 
        		(5, '1.1.2000 16:00')) as v(id, start_time)
        WHERE NOT EXISTS (SELECT 1 FROM vorrunden);
    """)
    
    # Insert tables when empty
    for letter in string.ascii_uppercase:
        cur.execute("""
            INSERT INTO tables (table_name)
            SELECT v.table_name
            FROM (VALUES (%s)) AS v(table_name)
            WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = %s)
        """, (letter,letter))

    # Insert matches only when matches is empty (one match per table)
    cur.execute("""
        INSERT INTO matches (table_id, vorrunde_id, finished)
        SELECT t.id, 1, TRUE
        FROM tables t
        WHERE NOT EXISTS (SELECT 1 FROM matches WHERE vorrunde_id=1)
        ORDER BY t.id
        LIMIT 3;
        INSERT INTO matches (table_id, vorrunde_id, finished)
        SELECT t.id, 2, TRUE
        FROM tables t
        WHERE NOT EXISTS (SELECT 1 FROM matches WHERE vorrunde_id=2)
        ORDER BY t.id
        LIMIT 3;
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
                WHEN p.username = 'Charlie1' THEN 15 + (r.round_number * 20)
                WHEN p.username = 'Charlie2' THEN 20 + (r.round_number * 10)
                WHEN p.username = 'Charlie3' THEN 20 + (r.round_number * 10)
                WHEN p.username = 'Charlie4' THEN 30 + (r.round_number * 10)
                WHEN p.username = 'Charlie5' THEN 35 + (r.round_number * 10)
                WHEN p.username = 'Charlie6' THEN -5 + (r.round_number * 10)
                WHEN p.username = 'Charlie7' THEN 15 + (r.round_number * 10)
            END
        FROM rounds r
        JOIN matches m ON r.match_id = m.id
        JOIN tables t ON m.table_id = t.id
        CROSS JOIN players p
        WHERE NOT EXISTS (SELECT 1 FROM round_results)
        AND (
            (t.table_name = 'A' AND p.username = 'Alice') OR
            (t.table_name = 'B' AND p.username = 'Bob') OR
            (t.table_name = 'C' AND p.username = 'Charlie1')OR
            (t.table_name = 'C' AND p.username = 'Charlie2')OR
            (t.table_name = 'C' AND p.username = 'Charlie3')OR
            (t.table_name = 'C' AND p.username = 'Charlie4')OR
            (t.table_name = 'C' AND p.username = 'Charlie5')OR
            (t.table_name = 'C' AND p.username = 'Charlie6')OR
            (t.table_name = 'A' AND p.username = 'Charlie7')
        )
    """)

    # Insert match_results with final standings and tournament points
    cur.execute("""
        INSERT INTO match_results (match_id, player_id, total_play_points, final_standing, tournament_points)
        WITH RankedResults AS (
            SELECT 
                match_id, 
                player_id, 
                play_points, 
                RANK() OVER (PARTITION BY match_id ORDER BY play_points DESC) AS standing
            FROM round_results 
            JOIN rounds r1 ON r1.id = round_id
            WHERE r1.round_number = (
                SELECT MAX(r2.round_number) 
                FROM rounds r2
                WHERE r1.match_id = r2.match_id
            )
        )
        SELECT 
            rr.match_id, 
            rr.player_id, 
            rr.play_points, 
            rr.standing, 
            tp.tp
        FROM RankedResults rr
        JOIN tournamentpoints_from_rank tp ON tp.rank = rr.standing;
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
    cur.execute('''
    DROP TABLE IF EXISTS round_results CASCADE;
    DROP TABLE IF EXISTS match_results CASCADE;
    DROP TABLE IF EXISTS rounds CASCADE;
    DROP TABLE IF EXISTS matches CASCADE;
    DROP TABLE IF EXISTS tables CASCADE;
    DROP TABLE IF EXISTS players CASCADE;
    DROP TABLE IF EXISTS vorrunden CASCADE;
    DROP TABLE IF EXISTS tiebreaker_results CASCADE;
    DROP TABLE IF EXISTS tournamentpoints_from_rank CASCADE;''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database dropped!\n"

