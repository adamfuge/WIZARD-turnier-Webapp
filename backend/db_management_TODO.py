#TODO: This file contains endpoints which MUST be removed before releasing, as they can e.g. wipe the entire database

from dotenv import load_dotenv
from app import app, get_db_connection

load_dotenv()