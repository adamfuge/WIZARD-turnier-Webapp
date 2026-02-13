# Endpoints for file serving and rendering
from dotenv import load_dotenv
from flask import send_from_directory
from app import app

load_dotenv()

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')