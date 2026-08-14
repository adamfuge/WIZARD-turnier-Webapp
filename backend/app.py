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

@app.route("/match_view/<string:match_id>")
def serve_match_view_table(match_id):
    return send_from_directory('../frontend', 'partietabelle.html')

@app.route("/tournament_view")
def serve_tournament_view():
    return send_from_directory('../frontend', 'turniertabelle.html')

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = None 
    if cur.description is not None:  
            result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

from contextlib import contextmanager 
@contextmanager
def get_db(): 
    """Stellt sicher, dass die Verbindung immer geschlossen wird.""" 
    conn = get_db_connection() 
    try: 
        yield conn 
        conn.commit() 
    except  Exception:
        conn.rollback()  
        raise
    finally: 
        conn.close() 

def recalculate_match_results(list_of_match_ids = []):
    with get_db() as conn: 
        cur = conn.cursor()
        if len(list_of_match_ids) == 0:
            cur.execute('''
                UPDATE match_results mr 
                SET total_play_points = (SELECT play_points
											FROM round_results rr1
            									JOIN rounds r1 ON r1.id = round_id
											WHERE r1.match_id = mr.match_id
											AND rr1.player_id = mr.player_id
            								AND r1.round_number = (
            								    SELECT MAX(r2.round_number) 
												FROM round_results rr2
            										JOIN rounds r2 ON r2.id = rr2.round_id
            								    WHERE r2.match_id = mr.match_id
												AND rr2.player_id = mr.player_id
												AND r2.finished
            								)),
					round_wins = (SELECT COUNT(lr.id) 
                                                        FROM rounds lr
                                                            JOIN rounds nr ON lr.match_id = nr.match_id
                                                            JOIN round_results l ON lr.id = l.round_id
                                                            JOIN round_results n ON nr.id = n.round_id 
                                                        WHERE l.player_id = n.player_id 
                                                        AND lr.round_number = nr.round_number-1
                                                        AND nr.finished
                                                        AND lr.match_id = mr.match_id
                                                        AND l.player_id = mr.player_id
                                                        AND n.play_points > l.play_points ),
                    best_round_result = (SELECT MAX(n.play_points - l.play_points) 
				                        FROM rounds lr
				                        	JOIN rounds nr ON lr.match_id = nr.match_id
				                        	JOIN round_results l ON lr.id = l.round_id
				                        	JOIN round_results n ON nr.id = n.round_id 
				                        WHERE l.player_id = n.player_id 
				                        AND lr.round_number = nr.round_number-1
				                        AND nr.finished
				                        AND lr.match_id = mr.match_id
				                        AND l.player_id = mr.player_id);

                UPDATE match_results mr 
				SET best_round_result_count = (SELECT COUNT(lr.id) 
				                        FROM rounds lr
				                        	JOIN rounds nr ON lr.match_id = nr.match_id
				                        	JOIN round_results l ON lr.id = l.round_id
				                        	JOIN round_results n ON nr.id = n.round_id 
				                        WHERE l.player_id = n.player_id 
				                        AND lr.round_number = nr.round_number-1
				                        AND nr.finished
				                        AND lr.match_id = mr.match_id
				                        AND l.player_id = mr.player_id
										AND n.play_points - l.play_points = best_round_result),
                     second_best_round_result = (SELECT MAX(n.play_points - l.play_points) 
				                        FROM rounds lr
				                        	JOIN rounds nr ON lr.match_id = nr.match_id
				                        	JOIN round_results l ON lr.id = l.round_id
				                        	JOIN round_results n ON nr.id = n.round_id 
				                        WHERE l.player_id = n.player_id 
				                        AND lr.round_number = nr.round_number-1
				                        AND nr.finished
				                        AND lr.match_id = mr.match_id
				                        AND l.player_id = mr.player_id
										AND n.play_points - l.play_points < best_round_result);
                    
                UPDATE tiebreaker_results
                SET play_points = CASE 
					WHEN prediction=tricks 
					THEN 20 + 10 * prediction 
					ELSE -10 * ABS(prediction-tricks)
				   END;

                WITH rankings AS (
                    SELECT 
                        id, 
                        RANK() OVER (
                            PARTITION BY tiebreaker_id 
                            ORDER BY play_points DESC) AS standing
                    FROM tiebreaker_results
                )
                UPDATE tiebreaker_results tr
                SET relative_standing = r.standing
                FROM rankings r
                WHERE tr.id = r.id; 
                                        
                UPDATE match_results mr 
                SET tiebreaker5_relative_standing = (SELECT relative_standing 
                                        FROM tiebreaker_results tr
                                        JOIN tiebreaker t ON tr.tiebreaker_id = t.id
                                        WHERE t.match_id = mr.match_id
                                        AND tr.player_id = mr.player_id)
                WHERE EXISTS (SELECT relative_standing 
                                        FROM tiebreaker_results tr
                                        JOIN tiebreaker t ON tr.tiebreaker_id = t.id
                                        WHERE t.match_id = mr.match_id
                                        AND tr.player_id = mr.player_id);

                UPDATE match_results mr 
				SET tiebreaker5_relative_standing = (SELECT relative_standing 
                                        FROM tiebreaker_results
                                        WHERE match_id = mr.match_id
				                        AND player_id = mr.player_id)
                WHERE EXISTS (SELECT relative_standing 
                                        FROM tiebreaker_results
                                        WHERE match_id = mr.match_id
				                        AND player_id = mr.player_id);

                    
                UPDATE match_results mr 
                SET tiebreaker5_relative_standing = 1
                WHERE NOT EXISTS (SELECT final_standing 
                                        FROM tiebreaker_results
                                        WHERE match_id = mr.match_id
                                        AND player_id = mr.player_id);

                WITH rankings as (SELECT id, RANK() OVER (PARTITION BY match_id 
														ORDER BY mr2.total_play_points DESC, 
                                        						 mr2.round_wins DESC,
																 mr2.best_round_result DESC,
																 mr2.best_round_result_count DESC,
																 mr2.second_best_round_result DESC,
																 mr2.tiebreaker5_relative_standing ASC
																 )
            											AS standing
											FROM match_results mr2)
                UPDATE match_results
                	SET final_standing = rankings.standing
                	FROM rankings
                WHERE match_results.id = rankings.id;

                WITH rankings as (SELECT id, RANK() OVER (PARTITION BY match_id 
														ORDER BY mr2.total_play_points DESC, 
                                        						 mr2.round_wins DESC,
																 mr2.best_round_result DESC,
																 mr2.best_round_result_count DESC,
																 mr2.second_best_round_result DESC,
																 mr2.tiebreaker5_relative_standing ASC
																 )
            											AS standing
											FROM match_results mr2)
                UPDATE match_results
                	SET final_standing = rankings.standing,
						tournament_points = tp
                	FROM rankings JOIN tournamentpoints_from_rank ON rankings.standing = rank
                WHERE match_results.id = rankings.id;

            ''')


@app.route("/tournament_data")
def tournament_data():

    recalculate_match_results()

    with get_db() as conn: 
        cur = conn.cursor()



        cur.execute('''
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
        result = cur.fetchall()
        
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

@app.route('/get_active_vorrunde', methods=['GET'])
def get_active_vorrunde():
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('''SELECT id, vorrunde_name 
                                    FROM vorrunden 
                                    WHERE id=(SELECT active_vorrunde_id 
                                                FROM active_vorrunde);''')
        result = cur.fetchall()

        return {'active_vorrunde_id': result[0][0], 'vorrunde_name': result[0][1]}

@app.route('/create_player', methods=['POST'])
def create_player():
    with get_db() as conn: 
        cur = conn.cursor()

        data = request.get_json()
        username = data.get('username')

        if not username:
            return "Error: 'username' is required.\n", 400
        
        cur.execute('INSERT INTO players (username) VALUES (%s);', (username,))
        return "Player created!\n"

@app.route('/create_player_by_id/<int:player_id>', methods=['GET'])
def create_player_by_id(player_id):
    with get_db() as conn: 
        cur = conn.cursor()
        
        cur.execute('INSERT INTO players (id,username) VALUES (%s,%s);', (player_id,player_id))
        return "Player created!\n"


@app.route('/get_players', methods=['GET'])
def get_players():
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('SELECT id, username, total_tournament_points, total_play_points FROM players;')
        result = cur.fetchall()

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
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('SELECT id, username, total_tournament_points, total_play_points FROM players WHERE id = %s;', (player_id,))
        result = cur.fetchall()
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
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('''
            SELECT p.id, p.username, p.total_tournament_points, p.total_play_points
            FROM players p
            JOIN tables t ON p.current_table_id = t.id
            WHERE t.table_name = %s;
        ''', (table_name,))
        result = cur.fetchall()

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
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}

        for result in data:
            table_name = result.get('table_name')
            player_id = result.get('player_id')
            play_points = result.get('play_points')
            tournament_points = result.get('tournament_points')

            cur.execute('''
                UPDATE match_results
                SET total_play_points = %s, tournament_points = %s
                WHERE match_id = (SELECT id FROM matches WHERE table_id = (SELECT id FROM tables WHERE table_name = %s))
                AND player_id = %s;
            ''', (play_points, tournament_points, table_name, player_id))

        return "Match results updated!\n"

@app.route('/post_tiebreaker_start', methods=['POST'])
def post_tiebreaker_start():
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match start is an object with the following structure:
        # {"vorrunde": 1, "table_name": "A", "spieler": [5,99,7]}

        table_name = data.get('table_name')
        vorrunde_id = data.get('vorrunde')
        match_id = data.get('match_id')
        player_ids = data.get('spieler')
        standing = data.get('umkaempfte_platzierung')


        if not vorrunde_id:
            cur.execute('''SELECT id, vorrunde_name 
                                            FROM vorrunden 
                                            WHERE id=(SELECT active_vorrunde_id 
                                                        FROM active_vorrunde);''')
            if cur.rowcount > 0:
                vorrunde_id = cur.fetchall()[0][0]
            else:
                vorrunde_id = 0
        
        
        if not match_id:
            cur.execute('''
                            SELECT id
                                                FROM matches 
                                                WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
                                                AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s)
                        ''', (table_name, vorrunde_id))
            match_id = cur.fetchall()[0][0]


        
        for player_id in player_ids:
            cur.execute('''
                        SELECT tiebreaker_id
                        FROM tiebreaker t 
                        JOIN tiebreaker_results tr ON t.id = tr.tiebreaker_id 
                        WHERE match_id = %s
                        AND player_id = %s
                        ''', (match_id,player_id,))

        if cur.rowcount > 0:
            return {'message':"Tiebreaker already started", 'tiebreaker_id':cur.fetchall()[0][0]}
        
        cur.execute('''
            INSERT INTO tiebreaker (match_id)
            VALUES (%s)
            RETURNING id
            ''', (match_id,))
        tiebreaker_id = cur.fetchall()[0][0]

        

        for player_id in player_ids:
            cur.execute('''
                        INSERT INTO tiebreaker_results (tiebreaker_id, player_id)
                        VALUES (%s,
                                %s)
                        RETURNING id
                        ''', (tiebreaker_id, player_id))
        

        return {'tiebreaker_id':tiebreaker_id}

@app.route('/post_tiebreaker_result', methods=['POST'])
def post_tiebreaker_result():
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}
            

        for result in data:
            table_name = result.get('tisch')
            vorrunde_id = result.get('vorrunde')
            player_id = result.get('spieler')
            prediction = result.get('schaetzungen')
            tricks = result.get('stiche')
            relative_standing = result.get('platzierung')

            cur.execute('''
                UPDATE tiebreaker_results
                SET prediction = %s,
                    tricks = %s
                FROM tiebreaker tb
                WHERE player_id = %s
                AND match_id =(SELECT m.id
                			FROM matches m
                			JOIN tables t ON t.id = m.table_id 
                			JOIN vorrunden v ON v.id = m.vorrunde_id 
                			WHERE table_name = %s
                			AND vorrunde_id = %s)
                RETURNING tiebreaker_id
            ''', (prediction, tricks, player_id, table_name, vorrunde_id))
            tiebreaker_id = cur.fetchall()[0][0]


            cur.execute('''
                UPDATE tiebreaker
                SET finished_at = CURRENT_TIMESTAMP,
                    finished = true
                wHERE id = %s
            ''', (tiebreaker_id, ))
        return "Tiebreaker results inserted!\n"

@app.route('/post_match_start', methods=['POST'])
def post_match_start():
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match start is an object with the following structure:
        # {"vorrunde": 1, "table_name": "A", "spieler": [5,99,7]}

        table_name = data.get('table_name')
        vorrunde_id = data.get('vorrunde')
        player_ids = data.get('spieler')
        first_dealer = data.get('erster_geber')


        if not vorrunde_id:
            cur.execute('''SELECT id, vorrunde_name 
                                            FROM vorrunden 
                                            WHERE id=(SELECT active_vorrunde_id 
                                                        FROM active_vorrunde);''')
            if cur.rowcount > 0:
                vorrunde_id = cur.fetchall()[0][0]
            else:
                vorrunde_id = 0
        
        cur.execute('''
            INSERT INTO matches (table_id, vorrunde_id)
            VALUES ((SELECT t.id FROM tables t WHERE table_name = %s),
            		(SELECT v.id FROM vorrunden v WHERE v.id = %s))
            RETURNING id
            ''', (table_name, vorrunde_id))
        match_id = cur.fetchall()[0][0]
        
        cur.execute('''
            INSERT INTO rounds (match_id, dealer_player_id, round_number)
            VALUES (%s,
                    %s,
                    1)
            RETURNING id
            ''', (match_id, first_dealer))
        round_id = cur.fetchall()[0][0]

        seat = 0
        for player_id in player_ids:
            seat = seat + 1
            cur.execute('''
                INSERT INTO match_results (match_id, player_id, seat)
                VALUES (%s,
                        %s,
                        %s)
            ''', (match_id, player_id, seat))
            cur.execute('''
                INSERT INTO round_results (round_id, player_id)
                VALUES (%s,
                        %s)
            ''', (round_id, player_id))
        

        return {'match_id':match_id}
    

@app.route('/post_match_update', methods=['POST'])
def post_match_update():
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match result is a JSON object containing like:
        # {"tisch": "A", "spieler": [1,2,3] ...
        last_round = data.get('letzte_runde')
        next_round = data.get('aktuelle_runde')
        
        cur.execute('''
            UPDATE rounds 
            SET finished_at = CURRENT_TIMESTAMP, finished = true
            WHERE match_id = (  SELECT id 
                                FROM matches 
                                WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
                                AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s))
            AND round_number = (SELECT round_number 
                                FROM round_numbers 
                                WHERE player_amount = %s
                                AND displayed_round_number = %s)
            RETURNING id;''', (data.get('tisch'),
                               data.get('vorrunde'),
                               len(data.get('spieler')), 
                               data.get('letzte_runde')))
        last_round_id = cur.fetchall()[0][0]

        if next_round:
            cur.execute('''
                        INSERT INTO rounds (match_id, dealer_player_id, round_number)
                                    VALUES ((  SELECT id 
                                                FROM matches 
                                                WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
                                                AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s)),
                                            %s,
                                            (SELECT round_number 
                                            FROM round_numbers 
                                            WHERE player_amount = %s
                                            AND displayed_round_number = %s))
                        RETURNING id;''', (data.get('tisch'),
                                           data.get('vorrunde'),
                                           data.get('geber')[next_round],
                                           len(data.get('spieler')), 
                                           next_round))
            next_round_id = cur.fetchall()[0][0]
        
        for i in range(len(data.get('spieler'))):
            player_id = data.get('spieler')[i]
            play_points = data.get('punktetabelle')[last_round][i]
            prediction = data.get('schaetzungen')[last_round][i]
            tricks = data.get('stiche')[last_round][i]
            
            cur.execute('''
                UPDATE round_results
                SET play_points = %s,
					prediction = %s,
					tricks = %s,
					submitted_at = CURRENT_TIMESTAMP
                WHERE round_id = %s
                AND player_id = %s
                RETURNING id;''', (play_points,
                                   prediction,
                                   tricks,
                                   last_round_id,
                                   player_id
                ))

            if next_round:
                cur.execute('''      
                    INSERT INTO round_results (round_id, player_id)
                    VALUES (%s,
                            %s)
                    RETURNING id''', ( next_round_id,
                                       player_id
                                ))
        

        return "Rounds results updated!\n"

# FIX PLS, something doppelt hier, logik nicht klar
@app.route('/post_match_result', methods=['POST'])
def post_match_result():
    with get_db() as conn: 
        cur = conn.cursor()
        data = request.get_json()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}

        
        cur.execute('''
            UPDATE matches 
            SET finished_at = CURRENT_TIMESTAMP, finished = true
            WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
            AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s)
            ''', (data[0].get('tisch'),data[0].get('vorrunde')))
        

        for result in data:
            match_id = result.get('match_id')
            table_name = result.get('tisch')
            vorrunde_id = result.get('vorrunde')
            player_id = result.get('spieler')
            play_points = result.get('partiepunkte')
            final_standing = result.get('platzierung')
            tournament_points = result.get('turnierpunkte')
            round_wins = result.get('plusrunden')

            if not match_id:
                cur.execute('''SELECT m.id
                			FROM matches m
                			JOIN tables t ON t.id = m.table_id 
                			JOIN vorrunden v ON v.id = m.vorrunde_id 
                			WHERE table_name = %s
                			AND vorrunde_id = %s''', (data[0].get('tisch'),data[0].get('vorrunde')))
                
                if cur.rowcount > 0:
                    match_id = cur.fetchall()[0][0]
                else:
                    return "match could not be found"
            
            cur.execute('''
                    UPDATE match_results 
                    SET total_play_points = %s,
                        final_standing = %s,
                        tournament_points = %s, 
                        round_wins = %s
                    WHERE match_id = %s
                    AND player_id = %s
                    RETURNING id
                ''', (play_points, 
                      final_standing, 
                      tournament_points, 
                      round_wins, 
                      match_id, 
                      player_id))


        return "Match results inserted!\n"

@app.route('/get_match_info/<int:match_id>', methods=['GET'])
def get_match_info(match_id):

    recalculate_match_results()

    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('''SELECT    vorrunde_id, 
                                                table_name
                                                FROM matches m, tables t
                                                WHERE m.id = %s
                                                AND t.id = m.table_id;
                                    ''', (match_id,))
        
        if cur.rowcount == 0:
            return "Match not found.\n", 404
        else:
            match_info = cur.fetchall()

        
        vorrunde = match_info[0][0]
        table_name = match_info[0][1]

        cur.execute('''SELECT   player_id, 
                                                username,
                                                final_standing
                                                FROM match_results mr, players p
                                                WHERE match_id = %s
                                                AND mr.player_id = p.id
                                                ORDER BY seat;
                                    ''', (match_id,))
        players_info = cur.fetchall()


        player_ids = []
        player_names = []
        player_standings = []

        for player_info in players_info:
            player_ids.append(player_info[0])
            player_names.append(player_info[1])
            player_standings.append(player_info[2])


        cur.execute('''SELECT    MAX(displayed_round_number)
                                                    FROM rounds r, round_numbers n
                                                    WHERE r.match_id = %s
                                                    AND r.finished = TRUE
                                                    AND r.round_number = n.round_number
                                                    AND n.player_amount = %s;
                                    ''', (match_id, len(player_ids)))
        last_round = cur.fetchall()[0][0]


        cur.execute('''SELECT    MIN(displayed_round_number)
                                                    FROM rounds r, round_numbers n
                                                    WHERE r.match_id = %s
                                                    AND r.finished = FALSE
                                                    AND r.round_number = n.round_number
                                                    AND n.player_amount = %s;
                                    ''', (match_id, len(player_ids)))
        next_round = cur.fetchall()[0][0]

        if next_round is not None and last_round is not None:
            scoressheet_length = last_round+1
            dealersheet_length = next_round+1
        elif last_round is not None:
            scoressheet_length = last_round+1
            dealersheet_length = last_round+1
        elif next_round is not None:
            scoressheet_length = next_round+1
            dealersheet_length = next_round+1
        else:
            return "Something went wrong regarding the scoresheet length"

        cur.execute('''SELECT   r.id, 
                                                displayed_round_number,
                                                dealer_player_id
                                                FROM rounds r, round_numbers n
                                                WHERE r.match_id = %s
                                                AND r.round_number = n.round_number
                                                AND n.player_amount = %s;
                                    ''', (match_id, len(player_ids)))
        rounds_info = cur.fetchall()



        displayed_round_numbers = []
        round_ids = []
        dealer = [None] * (dealersheet_length)

        for round_info in rounds_info:
            round_ids.append(round_info[0])
            displayed_round_numbers.append(round_info[1])
            dealer[round_info[1]] = round_info[2]



        if last_round is None:
            last_round = 0
            return {'vorrunde': vorrunde,
                        'tisch': table_name,
                        'spieler': list(map(str,player_ids)),
                        'punktetabelle': [[0]*len(player_ids)],
                        'letzte_runde': last_round,
                        'aktuelle_runde': next_round,
                        'schaetzungen': [[0]*len(player_ids)],
                        'stiche': [[0]*len(player_ids)],
                        'geber': list(map(str,dealer)),
                        'regeln': 'Turnier',
                        'platzierungen': [[1]*len(player_ids)]
                        }       

        cur.execute('''SELECT   seat, 
                                                        displayed_round_number,
                                                        prediction,
                                                        tricks,
                                                        play_points
                                                        FROM rounds r, round_results rr, match_results mr, round_numbers n
                                                        WHERE r.match_id = %s
                                                        AND mr.match_id = %s
                                                        AND rr.round_id = r.id
	    												AND r.round_number = n.round_number
                                                        AND rr.player_id = mr.player_id
                                                        AND n.player_amount = %s
                                                        AND finished = TRUE;
                                        ''', (match_id, match_id, len(player_ids)))
        round_results_infos = cur.fetchall()


        scores = [[None] * (len(player_ids)) for _ in range(scoressheet_length)]
        predictions = [[None] *(len(player_ids)) for _ in range(scoressheet_length)]
        tricks = [[None] * (len(player_ids)) for _ in range(scoressheet_length)]

        for res in round_results_infos:
            current_seat = res[0] - 1
            current_displayed_round_number = res[1]

            predictions[current_displayed_round_number][current_seat] = res[2]
            tricks[current_displayed_round_number][current_seat] = res[3]
            scores[current_displayed_round_number][current_seat] = res[4]

        cur.execute('''SELECT DISTINCT 1
                        FROM rounds
                        WHERE NOT finished
                        AND match_id = %s
                    ''', (match_id,))
        exists_unfinished_round = (cur.rowcount > 0)
        dump = cur.fetchall()

        cur.execute('''SELECT id
                        FROM tiebreaker
                        WHERE NOT finished
                        AND match_id = %s
                    ''', (match_id,))
        exists_unfinished_tiebreaker = (cur.rowcount > 0)
        unfinished_tiebreaker = cur.fetchall()

        tiebreaker_to_play = []
        for tiebreaker_id in unfinished_tiebreaker:
            cur.execute('''SELECT seat
                                    FROM tiebreaker_results tr
                                        JOIN tiebreaker t ON tr.tiebreaker_id = t.id
                                        JOIN match_results mr ON t.match_id = mr.match_id 
                                    WHERE t.id = %s
                                    AND tr.player_id = mr.player_id
                                ''', (tiebreaker_id,))
            tiebreaker_players = cur.fetchall()
            tiebreaker_to_play.append([n[0]-1 for n in tiebreaker_players])

        
        if last_round == 0:
            status = 'just_started'
        elif exists_unfinished_round:
            status = 'playing'
        elif exists_unfinished_tiebreaker:
            status = 'tiebreaker_missing'
        else: 
            status = 'finished'




        return {'match_id': match_id,
                'vorrunde': vorrunde,
                'tisch': table_name,
                'spieler': list(map(str,player_ids)),
                'punktetabelle': scores,
                'letzte_runde': last_round,
                'aktuelle_runde': next_round,
                'schaetzungen': predictions,
                'stiche': tricks,
                'geber': list(map(str,dealer)),
                'regeln': 'Turnier',
                'platzierungen': player_standings,
                'status': status,
                'ausstehende_tiebreaker': tiebreaker_to_play
                }           

@app.route('/get_table/<string:table_name>', methods=['GET'])
def get_table(table_name):
    with get_db() as conn: 
        cur = conn.cursor()

        cur.execute('SELECT id, table_name FROM tables WHERE table_name = %s;', (table_name,))
        result = cur.fetchall()

        if not result:
            return "Table not found.\n", 404
        table = result[0]
        return {
            'id': table[0],
            'table_name': table[1]
        }

@app.route('/get_tables', methods=['GET'])
def get_tables():
    with get_db() as conn: 
        cur = conn.cursor()

        cur.execute('SELECT id, table_name FROM tables;')
        result = cur.fetchall()

        tables_list = []
        for table in result:
            tables_list.append({
                'id': table[0],
                'table_name': table[1]
            })
        return {'tables': tables_list}

@app.route('/get_table_names', methods=['GET'])
def get_table_names():
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('SELECT table_name FROM tables;')
        result = cur.fetchall()

        tables_list = []
        for table in result:
            tables_list.append(table[0])
        return tables_list

@app.route('/get_available_table_names', methods=['GET'])
def get_available_table_names():
    with get_db() as conn: 
        cur = conn.cursor()
        cur.execute('''SELECT table_name 
                                    FROM tables t
                                    WHERE NOT EXISTS (SELECT 1 
                                                      FROM matches m, active_vorrunde
                                                      WHERE vorrunde_id=active_vorrunde_id
                                                      AND t.id = m.table_id)
	    							ORDER BY table_name ASC;''')
        result = cur.fetchall()

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
            vorrunde_name TEXT UNIQUE,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            CHECK (start_time <= end_time)
        );

        CREATE TABLE active_vorrunde (
            enforce_singleton CHAR(1) DEFAULT 'X' PRIMARY KEY CHECK (enforce_singleton = 'X'),
            active_vorrunde_id INT NOT NULL REFERENCES vorrunden(id) ON DELETE RESTRICT
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

        CREATE TABLE IF NOT EXISTS round_numbers (
            id SERIAL PRIMARY KEY,
            round_number INTEGER NOT NULL,
            player_amount INTEGER DEFAULT 0,
            displayed_round_number INTEGER NOT NULL,
            UNIQUE(round_number, player_amount)
        );

        CREATE TABLE IF NOT EXISTS rounds (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            round_number INTEGER NOT NULL,
            dealer_player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            finished BOOLEAN DEFAULT FALSE,
            UNIQUE (match_id, round_number)
        );

        CREATE TABLE IF NOT EXISTS round_results (
            id SERIAL PRIMARY KEY,
            round_id INTEGER NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            play_points INTEGER DEFAULT 0,
            prediction INTEGER,
            tricks INTEGER,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(round_id, player_id)
        );
        
        CREATE TABLE IF NOT EXISTS match_results (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            seat INTEGER CHECK(seat BETWEEN 1 AND 5),
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            total_play_points INTEGER DEFAULT 0,
            round_wins INTEGER DEFAULT 0,
            best_round_result INTEGER DEFAULT null,
            best_round_result_count INTEGER DEFAULT 0,
            second_best_round_result INTEGER DEFAULT null,
            tiebreaker5_relative_standing INTEGER DEFAULT 1,
            final_standing INTEGER DEFAULT 1,
            tournament_points INTEGER DEFAULT 0,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(match_id, player_id),
            UNIQUE(match_id, seat)
        );
                
        CREATE TABLE IF NOT EXISTS tiebreaker (
            id SERIAL PRIMARY KEY,
            match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,
            finished BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS tiebreaker_results (
            id SERIAL PRIMARY KEY,
            tiebreaker_id INTEGER NOT NULL REFERENCES tiebreaker(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            prediction INTEGER,
            tricks INTEGER,
            play_points INTEGER,
            relative_standing INTEGER,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tiebreaker_id, player_id)
        );

        CREATE TABLE IF NOT EXISTS penalties (
            id SERIAL PRIMARY KEY,
            round_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tournamentpoints_from_rank (
            rank SERIAL PRIMARY KEY,
            tp INTEGER NOT NULL
        );
    ''')
    cur.execute('''
        INSERT INTO vorrunden (id, vorrunde_name, start_time)
            SELECT v.id, v.vorrunde_name, to_timestamp(v.start_time, 'D.M.YYYY HH24:MI')
            FROM (VALUES (0, 'Pause', '1.1.2000 00:00')) as v(id, vorrunde_name, start_time)
            WHERE NOT EXISTS (SELECT 1 FROM vorrunden WHERE id=0)
        RETURNING id;

        INSERT INTO active_vorrunde (active_vorrunde_id)
            SELECT v.id 
            FROM vorrunden v
            WHERE vorrunde_name = 'Pause'
            AND NOT EXISTS (SELECT 1 FROM active_vorrunde)
        RETURNING active_vorrunde_id;

        INSERT INTO tournamentpoints_from_rank 
            SELECT * 
            FROM (VALUES (1,45),(2,30),(3,20),(4,10),(5,5))
            WHERE NOT EXISTS ( SELECT 1 FROM tournamentpoints_from_rank)
        RETURNING rank;

        INSERT INTO round_numbers (player_amount,round_number,displayed_round_number)
                    SELECT * 
                    FROM (VALUES    (4,1,1),
                                    (4,2,3),
                                    (4,3,5),
                                    (4,4,7),
                                    (4,5,9),
                                    (4,6,11),
                                    (4,7,12),
                                    (4,8,13),
                                    (4,9,14),
                                    (4,10,15),
                                    (3,1,2),
                                    (3,2,4),
                                    (3,3,6),
                                    (3,4,8),
                                    (3,5,10),
                                    (3,6,12),
                                    (3,7,14),
                                    (3,8,16),
                                    (3,9,18),
                                    (3,10,20),
                                    (5,1,2),
                                    (5,2,4),
                                    (5,3,5),
                                    (5,4,6),
                                    (5,5,7),
                                    (5,6,8),
                                    (5,7,9),
                                    (5,8,10),
                                    (5,9,11),
                                    (5,10,12))
                    WHERE NOT EXISTS ( SELECT 1 FROM round_numbers)
                RETURNING id;
    ''')
    for letter in string.ascii_uppercase:
                cur.execute("""
                    INSERT INTO tables (table_name)
                    SELECT v.table_name
                    FROM (VALUES (%s)) AS v(table_name)
                    WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = %s)
                """, (letter,letter))
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
    with get_db() as conn: 
        cur = conn.cursor()
        # the match result is an array of objects, each object has the following structure:
        # {"table_name": "A", "player_id": 1, "play_points": 5, "tournament_points": 10}
        
        
        # Insert vorrunden
        cur.execute("""
            INSERT INTO vorrunden (id, start_time)
            SELECT v.id, to_timestamp(v.start_time, 'D.M.YYYY HH24:MI')
            FROM (VALUES (1, '1.1.2003 12:00'), 
            		(2, '1.1.2003 14:00'), 
            		(3, '1.1.2003 16:00'), 
            		(5, '1.1.2000 16:00')) as v(id, start_time)
            WHERE NOT EXISTS (SELECT 1 FROM vorrunden WHERE id <> 0)
        """)
        
        for letter in string.ascii_uppercase:
            cur.execute("""
                INSERT INTO tables (table_name)
                SELECT v.table_name
                FROM (VALUES (%s)) AS v(table_name)
                WHERE NOT EXISTS (SELECT 1 FROM tables WHERE table_name = %s)
            """, (letter,letter))

        
        data = [
                {"vorrunde": 1,'tisch':'A','spieler': 94,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'A','spieler': 46,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 1,'tisch':'A','spieler': 15,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'A','spieler': 36,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 1,'tisch':'B','spieler': 64,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'B','spieler': 90,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'B','spieler': 30,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 3},{"vorrunde": 1,'tisch':'B','spieler': 49,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'C','spieler': 77,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'C','spieler': 73,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'C','spieler': 10,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 1,'tisch':'C','spieler': 89,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'D','spieler': 31,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'D','spieler': 5,'turnierpunkte': 30,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'D','spieler': 67,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'D','spieler': 58,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 5},{"vorrunde": 1,'tisch':'E','spieler': 13,'turnierpunkte': 45,'partiepunkte': 210,'plusrunden': 4},{"vorrunde": 1,'tisch':'E','spieler': 40,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 3},{"vorrunde": 1,'tisch':'E','spieler': 50,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 4},{"vorrunde": 1,'tisch':'E','spieler': 8,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'F','spieler': 24,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 1,'tisch':'F','spieler': 51,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 6},{"vorrunde": 1,'tisch':'F','spieler': 14,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 1,'tisch':'F','spieler': 45,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 1,'tisch':'G','spieler': 21,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'G','spieler': 35,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 6},{"vorrunde": 1,'tisch':'G','spieler': 53,'turnierpunkte': 20,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'G','spieler': 2,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'H','spieler': 63,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 1,'tisch':'H','spieler': 6,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 7},{"vorrunde": 1,'tisch':'H','spieler': 102,'turnierpunkte': 45,'partiepunkte': 360,'plusrunden': 9},{"vorrunde": 1,'tisch':'H','spieler': 54,'turnierpunkte': 20,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'I','spieler': 92,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 1,'tisch':'I','spieler': 87,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'I','spieler': 84,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'I','spieler': 82,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 1,'tisch':'J','spieler': 75,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'J','spieler': 60,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 1,'tisch':'J','spieler': 97,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'J','spieler': 80,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 1,'tisch':'K','spieler': 72,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 5},{"vorrunde": 1,'tisch':'K','spieler': 16,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'K','spieler': 78,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'K','spieler': 42,'turnierpunkte': 45,'partiepunkte': 380,'plusrunden': 9},{"vorrunde": 1,'tisch':'L','spieler': 37,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 1,'tisch':'L','spieler': 4,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'L','spieler': 26,'turnierpunkte': 20,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'L','spieler': 52,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 10},{"vorrunde": 1,'tisch':'M','spieler': 11,'turnierpunkte': 30,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 1,'tisch':'M','spieler': 98,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 1,'tisch':'M','spieler': 17,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 1,'tisch':'M','spieler': 33,'turnierpunkte': 45,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 1,'tisch':'N','spieler': 68,'turnierpunkte': 45,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 1,'tisch':'N','spieler': 96,'turnierpunkte': 20,'partiepunkte': 50,'plusrunden': 3},{"vorrunde": 1,'tisch':'N','spieler': 12,'turnierpunkte': 30,'partiepunkte': 60,'plusrunden': 3},{"vorrunde": 1,'tisch':'N','spieler': 41,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 1,'tisch':'O','spieler': 101,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 8},{"vorrunde": 1,'tisch':'O','spieler': 32,'turnierpunkte': 20,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 1,'tisch':'O','spieler': 25,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 1,'tisch':'O','spieler': 18,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 19,'turnierpunkte': 10,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 47,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'P','spieler': 7,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 1,'tisch':'P','spieler': 9,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'Q','spieler': 55,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'Q','spieler': 79,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'Q','spieler': 62,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'Q','spieler': 38,'turnierpunkte': 45,'partiepunkte': 420,'plusrunden': 9},{"vorrunde": 1,'tisch':'R','spieler': 81,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'R','spieler': 59,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'R','spieler': 43,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 1,'tisch':'R','spieler': 66,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'S','spieler': 22,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'S','spieler': 83,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 1,'tisch':'S','spieler': 93,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 1,'tisch':'S','spieler': 39,'turnierpunkte': 10,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'T','spieler': 1,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 7},{"vorrunde": 1,'tisch':'T','spieler': 27,'turnierpunkte': 10,'partiepunkte': -20,'plusrunden': 3},{"vorrunde": 1,'tisch':'T','spieler': 34,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 1,'tisch':'T','spieler': 57,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 1,'tisch':'U','spieler': 88,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 1,'tisch':'U','spieler': 76,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 1,'tisch':'U','spieler': 20,'turnierpunkte': 10,'partiepunkte': -10,'plusrunden': 4},{"vorrunde": 1,'tisch':'U','spieler': 100,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 1,'tisch':'V','spieler': 29,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 1,'tisch':'V','spieler': 48,'turnierpunkte': 20,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 1,'tisch':'V','spieler': 91,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 1,'tisch':'V','spieler': 23,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 1,'tisch':'W','spieler': 61,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 1,'tisch':'W','spieler': 65,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 1,'tisch':'W','spieler': 95,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 1,'tisch':'W','spieler': 71,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 1,'tisch':'X','spieler': 56,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 1,'tisch':'X','spieler': 3,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 1,'tisch':'X','spieler': 70,'turnierpunkte': 10,'partiepunkte': 40,'plusrunden': 4},{"vorrunde": 1,'tisch':'X','spieler': 99,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 1,'tisch':'Y','spieler': 44,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 1,'tisch':'Y','spieler': 86,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 7},{"vorrunde": 1,'tisch':'Y','spieler': 103,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 9},{"vorrunde": 1,'tisch':'Y','spieler': 28,'turnierpunkte': 10,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 74,'turnierpunkte': 10,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 69,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 1,'tisch':'Z','spieler': 104,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 1,'tisch':'Z','spieler': 85,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 8}
,
{"vorrunde": 2,'tisch':'A','spieler': 51,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'A','spieler': 81,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'A','spieler': 4,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 8},{"vorrunde": 2,'tisch':'A','spieler': 94,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 2,'tisch':'B','spieler': 36,'turnierpunkte': 30,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 2,'tisch':'B','spieler': 53,'turnierpunkte': 45,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'B','spieler': 66,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'B','spieler': 37,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 2,'tisch':'C','spieler': 46,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'C','spieler': 2,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 2,'tisch':'C','spieler': 11,'turnierpunkte': 45,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'C','spieler': 43,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 2,'tisch':'D','spieler': 15,'turnierpunkte': 45,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 21,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 98,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 5},{"vorrunde": 2,'tisch':'D','spieler': 83,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'E','spieler': 17,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 5},{"vorrunde": 2,'tisch':'E','spieler': 93,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 2,'tisch':'E','spieler': 49,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 2,'tisch':'E','spieler': 35,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 2,'tisch':'F','spieler': 54,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'F','spieler': 33,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 2,'tisch':'F','spieler': 22,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'F','spieler': 64,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 2,'tisch':'G','spieler': 90,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'G','spieler': 63,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'G','spieler': 39,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 2,'tisch':'G','spieler': 96,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 2,'tisch':'H','spieler': 30,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 2,'tisch':'H','spieler': 68,'turnierpunkte': 10,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 2,'tisch':'H','spieler': 6,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 2,'tisch':'H','spieler': 70,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'I','spieler': 10,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'I','spieler': 41,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 5},{"vorrunde": 2,'tisch':'I','spieler': 57,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 7},{"vorrunde": 2,'tisch':'I','spieler': 102,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'J','spieler': 12,'turnierpunkte': 45,'partiepunkte': 390,'plusrunden': 9},{"vorrunde": 2,'tisch':'J','spieler': 89,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'J','spieler': 71,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 2,'tisch':'J','spieler': 92,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'K','spieler': 87,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 2,'tisch':'K','spieler': 25,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'K','spieler': 77,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 10},{"vorrunde": 2,'tisch':'K','spieler': 1,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'L','spieler': 84,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'L','spieler': 18,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'L','spieler': 76,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 2,'tisch':'L','spieler': 73,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 2,'tisch':'M','spieler': 5,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'M','spieler': 82,'turnierpunkte': 30,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'M','spieler': 101,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'M','spieler': 27,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 4},{"vorrunde": 2,'tisch':'N','spieler': 67,'turnierpunkte': 45,'partiepunkte': 350,'plusrunden': 8},{"vorrunde": 2,'tisch':'N','spieler': 20,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 6},{"vorrunde": 2,'tisch':'N','spieler': 60,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'N','spieler': 32,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 2,'tisch':'O','spieler': 58,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 2,'tisch':'O','spieler': 100,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'O','spieler': 75,'turnierpunkte': 45,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 2,'tisch':'O','spieler': 7,'turnierpunkte': 30,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'P','spieler': 80,'turnierpunkte': 30,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 2,'tisch':'P','spieler': 9,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 2,'tisch':'P','spieler': 3,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 2,'tisch':'P','spieler': 31,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 2,'tisch':'Q','spieler': 97,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 2,'tisch':'Q','spieler': 13,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 2,'tisch':'Q','spieler': 29,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 2,'tisch':'Q','spieler': 47,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 26,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 38,'turnierpunkte': 45,'partiepunkte': 160,'plusrunden': 6},{"vorrunde": 2,'tisch':'R','spieler': 56,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 2,'tisch':'R','spieler': 24,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 2,'tisch':'S','spieler': 50,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 2,'tisch':'S','spieler': 42,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 2,'tisch':'S','spieler': 55,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 2,'tisch':'S','spieler': 48,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 2,'tisch':'T','spieler': 8,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 2,'tisch':'T','spieler': 72,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 5},{"vorrunde": 2,'tisch':'T','spieler': 79,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 10},{"vorrunde": 2,'tisch':'T','spieler': 86,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 2,'tisch':'U','spieler': 16,'turnierpunkte': 30,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 2,'tisch':'U','spieler': 62,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 2,'tisch':'U','spieler': 65,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 10},{"vorrunde": 2,'tisch':'U','spieler': 14,'turnierpunkte': 20,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 2,'tisch':'V','spieler': 40,'turnierpunkte': 45,'partiepunkte': 270,'plusrunden': 7},{"vorrunde": 2,'tisch':'V','spieler': 78,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 2,'tisch':'V','spieler': 44,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 2,'tisch':'V','spieler': 91,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 2,'tisch':'W','spieler': 85,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 2,'tisch':'W','spieler': 45,'turnierpunkte': 45,'partiepunkte': 120,'plusrunden': 6},{"vorrunde": 2,'tisch':'W','spieler': 59,'turnierpunkte': 20,'partiepunkte': 100,'plusrunden': 5},{"vorrunde": 2,'tisch':'W','spieler': 95,'turnierpunkte': 10,'partiepunkte': 100,'plusrunden': 4},{"vorrunde": 2,'tisch':'X','spieler': 34,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 2,'tisch':'X','spieler': 88,'turnierpunkte': 30,'partiepunkte': 380,'plusrunden': 10},{"vorrunde": 2,'tisch':'X','spieler': 61,'turnierpunkte': 20,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 2,'tisch':'X','spieler': 74,'turnierpunkte': 45,'partiepunkte': 430,'plusrunden': 9},{"vorrunde": 2,'tisch':'Y','spieler': 52,'turnierpunkte': 45,'partiepunkte': 410,'plusrunden': 9},{"vorrunde": 2,'tisch':'Y','spieler': 19,'turnierpunkte': 10,'partiepunkte': 70,'plusrunden': 4},{"vorrunde": 2,'tisch':'Y','spieler': 69,'turnierpunkte': 20,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 2,'tisch':'Y','spieler': 103,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 2,'tisch':'Z','spieler': 28,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 2,'tisch':'Z','spieler': 99,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 2,'tisch':'Z','spieler': 23,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 2,'tisch':'Z','spieler': 104,'turnierpunkte': 45,'partiepunkte': 370,'plusrunden': 8}
,
{"vorrunde": 3,'tisch':'A','spieler': 49,'turnierpunkte': 45,'partiepunkte': 350,'plusrunden': 8},{"vorrunde": 3,'tisch':'A','spieler': 94,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 3,'tisch':'A','spieler': 5,'turnierpunkte': 10,'partiepunkte': 120,'plusrunden': 4},{"vorrunde": 3,'tisch':'A','spieler': 10,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 7},{"vorrunde": 3,'tisch':'B','spieler': 14,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 3,'tisch':'B','spieler': 54,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'B','spieler': 13,'turnierpunkte': 30,'partiepunkte': 250,'plusrunden': 6},{"vorrunde": 3,'tisch':'B','spieler': 53,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'C','spieler': 60,'turnierpunkte': 10,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 3,'tisch':'C','spieler': 26,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 5},{"vorrunde": 3,'tisch':'C','spieler': 92,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'C','spieler': 78,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 3,'tisch':'D','spieler': 96,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 3,'tisch':'D','spieler': 7,'turnierpunkte': 45,'partiepunkte': 320,'plusrunden': 7},{"vorrunde": 3,'tisch':'D','spieler': 11,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 4},{"vorrunde": 3,'tisch':'D','spieler': 25,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'E','spieler': 59,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 3,'tisch':'E','spieler': 70,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 3,'tisch':'E','spieler': 83,'turnierpunkte': 20,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 3,'tisch':'E','spieler': 55,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 8},{"vorrunde": 3,'tisch':'F','spieler': 48,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 8},{"vorrunde": 3,'tisch':'F','spieler': 56,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'F','spieler': 85,'turnierpunkte': 10,'partiepunkte': 110,'plusrunden': 4},{"vorrunde": 3,'tisch':'F','spieler': 88,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 5},{"vorrunde": 3,'tisch':'G','spieler': 89,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 6},{"vorrunde": 3,'tisch':'G','spieler': 64,'turnierpunkte': 10,'partiepunkte': 40,'plusrunden': 3},{"vorrunde": 3,'tisch':'G','spieler': 40,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'G','spieler': 67,'turnierpunkte': 20,'partiepunkte': 70,'plusrunden': 3},{"vorrunde": 3,'tisch':'H','spieler': 2,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 3,'tisch':'H','spieler': 74,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'H','spieler': 87,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 8},{"vorrunde": 3,'tisch':'H','spieler': 63,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 3,'tisch':'I','spieler': 42,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'I','spieler': 75,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 3,'tisch':'I','spieler': 52,'turnierpunkte': 20,'partiepunkte': 120,'plusrunden': 5},{"vorrunde": 3,'tisch':'I','spieler': 98,'turnierpunkte': 10,'partiepunkte': 0,'plusrunden': 3},{"vorrunde": 3,'tisch':'J','spieler': 18,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 3,'tisch':'J','spieler': 68,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'J','spieler': 9,'turnierpunkte': 20,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 3,'tisch':'J','spieler': 79,'turnierpunkte': 10,'partiepunkte': 130,'plusrunden': 5},{"vorrunde": 3,'tisch':'K','spieler': 93,'turnierpunkte': 10,'partiepunkte': 80,'plusrunden': 5},{"vorrunde": 3,'tisch':'K','spieler': 69,'turnierpunkte': 45,'partiepunkte': 290,'plusrunden': 7},{"vorrunde": 3,'tisch':'K','spieler': 81,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 3,'tisch':'K','spieler': 76,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 65,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 46,'turnierpunkte': 10,'partiepunkte': 20,'plusrunden': 3},{"vorrunde": 3,'tisch':'L','spieler': 90,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 7},{"vorrunde": 3,'tisch':'L','spieler': 3,'turnierpunkte': 20,'partiepunkte': 150,'plusrunden': 6},{"vorrunde": 3,'tisch':'M','spieler': 45,'turnierpunkte': 20,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'M','spieler': 77,'turnierpunkte': 30,'partiepunkte': 190,'plusrunden': 7},{"vorrunde": 3,'tisch':'M','spieler': 58,'turnierpunkte': 10,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'M','spieler': 50,'turnierpunkte': 45,'partiepunkte': 390,'plusrunden': 8},{"vorrunde": 3,'tisch':'N','spieler': 6,'turnierpunkte': 20,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 3,'tisch':'N','spieler': 80,'turnierpunkte': 10,'partiepunkte': 60,'plusrunden': 4},{"vorrunde": 3,'tisch':'N','spieler': 21,'turnierpunkte': 30,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'N','spieler': 84,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'O','spieler': 4,'turnierpunkte': 45,'partiepunkte': 400,'plusrunden': 10},{"vorrunde": 3,'tisch':'O','spieler': 17,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 5},{"vorrunde": 3,'tisch':'O','spieler': 41,'turnierpunkte': 10,'partiepunkte': 160,'plusrunden': 4},{"vorrunde": 3,'tisch':'O','spieler': 72,'turnierpunkte': 30,'partiepunkte': 280,'plusrunden': 3},{"vorrunde": 3,'tisch':'P','spieler': 47,'turnierpunkte': 20,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 3,'tisch':'P','spieler': 66,'turnierpunkte': 30,'partiepunkte': 310,'plusrunden': 7},{"vorrunde": 3,'tisch':'P','spieler': 62,'turnierpunkte': 10,'partiepunkte': 50,'plusrunden': 4},{"vorrunde": 3,'tisch':'P','spieler': 101,'turnierpunkte': 45,'partiepunkte': 330,'plusrunden': 8},{"vorrunde": 3,'tisch':'Q','spieler': 33,'turnierpunkte': 10,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 37,'turnierpunkte': 45,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 32,'turnierpunkte': 30,'partiepunkte': 240,'plusrunden': 7},{"vorrunde": 3,'tisch':'Q','spieler': 12,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'R','spieler': 73,'turnierpunkte': 20,'partiepunkte': 90,'plusrunden': 4},{"vorrunde": 3,'tisch':'R','spieler': 15,'turnierpunkte': 30,'partiepunkte': 160,'plusrunden': 5},{"vorrunde": 3,'tisch':'R','spieler': 30,'turnierpunkte': 45,'partiepunkte': 280,'plusrunden': 5},{"vorrunde": 3,'tisch':'R','spieler': 61,'turnierpunkte': 0,'partiepunkte': 0,'plusrunden': 0},{"vorrunde": 3,'tisch':'S','spieler': 35,'turnierpunkte': 45,'partiepunkte': 340,'plusrunden': 8},{"vorrunde": 3,'tisch':'S','spieler': 8,'turnierpunkte': 30,'partiepunkte': 260,'plusrunden': 7},{"vorrunde": 3,'tisch':'S','spieler': 31,'turnierpunkte': 10,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'S','spieler': 51,'turnierpunkte': 20,'partiepunkte': 250,'plusrunden': 7},{"vorrunde": 3,'tisch':'T','spieler': 102,'turnierpunkte': 45,'partiepunkte': 230,'plusrunden': 7},{"vorrunde": 3,'tisch':'T','spieler': 97,'turnierpunkte': 20,'partiepunkte': 200,'plusrunden': 6},{"vorrunde": 3,'tisch':'T','spieler': 28,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 6},{"vorrunde": 3,'tisch':'T','spieler': 16,'turnierpunkte': 10,'partiepunkte': 190,'plusrunden': 5},{"vorrunde": 3,'tisch':'U','spieler': 38,'turnierpunkte': 20,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'U','spieler': 43,'turnierpunkte': 30,'partiepunkte': 300,'plusrunden': 7},{"vorrunde": 3,'tisch':'U','spieler': 19,'turnierpunkte': 45,'partiepunkte': 340,'plusrunden': 8},{"vorrunde": 3,'tisch':'U','spieler': 44,'turnierpunkte': 10,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'V','spieler': 71,'turnierpunkte': 10,'partiepunkte': 30,'plusrunden': 3},{"vorrunde": 3,'tisch':'V','spieler': 22,'turnierpunkte': 30,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'V','spieler': 91,'turnierpunkte': 20,'partiepunkte': 290,'plusrunden': 8},{"vorrunde": 3,'tisch':'V','spieler': 20,'turnierpunkte': 45,'partiepunkte': 310,'plusrunden': 8},{"vorrunde": 3,'tisch':'W','spieler': 86,'turnierpunkte': 30,'partiepunkte': 220,'plusrunden': 5},{"vorrunde": 3,'tisch':'W','spieler': 29,'turnierpunkte': 20,'partiepunkte': 180,'plusrunden': 6},{"vorrunde": 3,'tisch':'W','spieler': 27,'turnierpunkte': 10,'partiepunkte': 140,'plusrunden': 6},{"vorrunde": 3,'tisch':'W','spieler': 99,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'X','spieler': 23,'turnierpunkte': 30,'partiepunkte': 170,'plusrunden': 5},{"vorrunde": 3,'tisch':'X','spieler': 1,'turnierpunkte': 45,'partiepunkte': 240,'plusrunden': 6},{"vorrunde": 3,'tisch':'X','spieler': 95,'turnierpunkte': 20,'partiepunkte': 140,'plusrunden': 4},{"vorrunde": 3,'tisch':'X','spieler': 100,'turnierpunkte': 0,'partiepunkte': 0,'plusrunden': 0},{"vorrunde": 3,'tisch':'Y','spieler': 82,'turnierpunkte': 10,'partiepunkte': 150,'plusrunden': 5},{"vorrunde": 3,'tisch':'Y','spieler': 39,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'Y','spieler': 103,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'Y','spieler': 34,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 7},{"vorrunde": 3,'tisch':'Z','spieler': 104,'turnierpunkte': 45,'partiepunkte': 220,'plusrunden': 5},{"vorrunde": 3,'tisch':'Z','spieler': 36,'turnierpunkte': 20,'partiepunkte': 190,'plusrunden': 6},{"vorrunde": 3,'tisch':'Z','spieler': 24,'turnierpunkte': 30,'partiepunkte': 210,'plusrunden': 6},{"vorrunde": 3,'tisch':'Z','spieler': 57,'turnierpunkte': 10,'partiepunkte': -190,'plusrunden': 4}


                ]
        seat_counter = 0

        for result in data:
            table_name = result.get('tisch')
            vorrunde_id = result.get('vorrunde')
            player_id = result.get('spieler')
            play_points = result.get('partiepunkte')
            final_standing = result.get('platzierung')
            tournament_points = result.get('turnierpunkte')
            round_wins = result.get('plusrunden')

            seat_counter = seat_counter % 4 + 1

            cur.execute('''
                INSERT INTO players (id, username)
                SELECT * 
                FROM (VALUES (%s,%s))
                WHERE NOT EXISTS (SELECT 1 FROM players WHERE id = %s)
            ''', (player_id, player_id, player_id))

            cur.execute('''
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
            match_id = cur.fetchall()

            if not match_id:
                cur.execute('''
                                SELECT id
                                                    FROM matches 
                                                    WHERE table_id = (SELECT t.id FROM tables t WHERE table_name = %s)
                                                    AND vorrunde_id = (SELECT v.id FROM vorrunden v WHERE v.id = %s)
                            ''', (table_name, vorrunde_id))
                match_id = cur.fetchall()
            
            cur.execute('''
                INSERT INTO match_results (match_id, player_id, total_play_points, final_standing, tournament_points, round_wins, seat)
                VALUES (%s,
                		%s,
                		%s,
                		%s,
                		%s,
                		%s,
                		%s)
            ''', (match_id[0][0], player_id, play_points, final_standing, tournament_points, round_wins, seat_counter))

            cur.execute('''
                INSERT INTO rounds (match_id, dealer_player_id, round_number, finished)
                SELECT * 
                FROM (VALUES (%s,%s,1,TRUE),(%s,%s,2,TRUE),(%s,%s,3,FALSE))
                WHERE NOT EXISTS (SELECT 1 
                                    FROM rounds 
                                    WHERE match_id = %s)
                RETURNING id;
            ''', (match_id[0][0], player_id, match_id[0][0], player_id, match_id[0][0], player_id, match_id[0][0]))
            round_id = cur.fetchall()

            if not round_id:
                cur.execute('''SELECT id
                                            FROM rounds 
                                            WHERE match_id = %s
                                            AND match_id = %s
                                        ''', (match_id[0][0],match_id[0][0]))
                round_id = cur.fetchall()
            
            cur.execute('''
                INSERT INTO round_results (round_id, player_id, play_points)
                VALUES (%s, %s, 0),
                       (%s, %s, %s),
                       (%s, %s, 0)
            ''', (round_id[0][0], player_id, round_id[1][0], player_id, play_points, round_id[2][0], player_id))

            cur.execute('''
                INSERT INTO tiebreaker (id,match_id) 
                VALUES (1, (SELECT m.id FROM matches m, tables t WHERE m.table_id=t.id AND t.table_name='L' AND vorrunde_id = 1))
            ''')
            
            cur.execute('''
            INSERT INTO tiebreaker_results (tiebreaker_id, 
								player_id, 
								prediction, 
								tricks) 
                VALUES (1, 26, 3, 3),
						(1, 4, 3, 2)
            ''')
                        
        return "Match results updated!\n"

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
    DROP TABLE IF EXISTS active_vorrunde CASCADE;
    DROP TABLE IF EXISTS tiebreaker CASCADE;
    DROP TABLE IF EXISTS tiebreaker_results CASCADE;
    DROP TABLE IF EXISTS penalties CASCADE;
    DROP TABLE IF EXISTS tournamentpoints_from_rank CASCADE;
    DROP TABLE IF EXISTS round_numbers CASCADE;''')
    conn.commit()
    cur.close()
    conn.close()
    return "Database dropped!\n"

