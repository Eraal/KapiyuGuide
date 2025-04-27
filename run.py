import sys
from flask_socketio import SocketIO
from pathlib import Path


sys.path.append(str(Path(__file__).parent))

from app import create_app, socketio


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True) 