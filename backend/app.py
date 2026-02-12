import time


from flask import Flask

app = Flask(__name__)

def get_hit_count():
    return 5

@app.route('/')
def hello():
    count = get_hit_count()
    return f'Hello World! I have been seen {count} times.\n'