from dotenv import load_dotenv
from flask import request
from app import app, get_db_connection

load_dotenv()

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