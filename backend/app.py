from flask import Flask
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

@app.route('/api')
def api():
    return {"message": f"Hello from {socket.gethostname()}"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)