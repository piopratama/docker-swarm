import os
from flask import Flask, session, jsonify
from flask_session import Session
import redis
import os
from flask_cors import CORS
import socket

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# CORS fix: support credentials (cookies)
CORS(app, supports_credentials=True)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

# Redis untuk session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.StrictRedis(host=REDIS_HOST, port=6379)
app.config['SESSION_PERMANENT'] = False

Session(app)

@app.route('/api')
def index():
    session['counter'] = session.get('counter', 0) + 1
    return jsonify(
        message="Hello from Flask!",
        counter=session['counter'],
        hostname=socket.gethostname()
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
