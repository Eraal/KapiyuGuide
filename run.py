import eventlet
eventlet.monkey_patch()

import sys
from pathlib import Path
from app import create_app
from app.extensions import socketio
import eventlet

sys.path.append(str(Path(__file__).parent))

app = create_app()

if __name__ == '__main__':
    # Use eventlet WSGI server
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)