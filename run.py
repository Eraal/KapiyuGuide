import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)