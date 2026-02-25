# Endpoints
This file is intended as an exhaustive list of endpoints available for the fronend with the fitting request and result

## Template renderer
these are stored in `render.py`


## Database operations
- `GET /init_db`
    - initializes the database schema (creates tables if they do not exist)
    - returns a simple text response indicating success or failure
- `GET /dump_db`
    - debug endpoint that returns the current rows from `players` and `tournaments` tables in plain text format
    - should not be exposed in production
- `GET /populate_db_examples`
    - populates the database with example data (only if tables are empty)
    - returns a text response indicating that example data has been ensured
- `GET /reset_db`
    - resets the database by deleting all data from tables
    - returns a text response confirming the reset
- `GET /drop_db`
    - drops all tables in the database (dangerous operation)
    - returns a text response confirming the drop

## Frontend
- `GET /`
    - serves the frontend `index.html` from the `frontend` folder
    - this is the main entry point for users accessing the webapp through a browser
    - additional frontend-related endpoints may be added in the future as needed by the frontend application

## get_and_set_endpoints
- `GET /get_players`
    - retrieves a list of all players from the database
    - returns a JSON response containing a list of player objects with id, username, sum_tournament_points, and sum_play_points
- `POST /create_player`
    - adds a new player to the database
    - expects a JSON payload with 'username' field
    - returns a text response confirming the creation or an error message
- `GET /get_player/<int:player_id>`
    - retrieves details of a specific player by ID
    - expects the player ID in the URL path
    - returns a JSON response with player details or 404 if not found
- `GET /get_players_by_table/<string:table_name>`
    - retrieves a list of players assigned to a specific table
    - expects the table name in the URL path
    - returns a JSON response containing a list of player objects
- `POST /update_player_status`
    - updates the active status and current table of a player
    - expects a JSON payload with 'player_id', 'is_active', and 'current_table' fields
    - returns a text response confirming the update or an error message
- `POST /post_match_result`
    - updates match results for players
    - expects a JSON array of objects, each with 'table_name', 'player_id', 'play_points', and 'tournament_points'
    - returns a text response confirming the update or an error message
- `GET /get_table/<string:table_name>`
    - retrieves details of a specific table by name
    - expects the table name in the URL path
    - returns a JSON response with table details or 404 if not found
- `GET /get_tables`
    - retrieves a list of all tables from the database
    - returns a JSON response containing a list of table objects with id and table_name


