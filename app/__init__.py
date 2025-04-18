from flask import Flask 
from .extensions import db
from pathlib import Path
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    root_path = Path(__file__).parent.parent

    app = Flask(__name__
                , template_folder=str(root_path / "templates"),
                static_folder=str(root_path / "static")
                )
    app.config.from_object('config.Config')

    
    db.init_app(app)
    
    # Register all blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .admin.routes import admin_bp
    from .office.routes import office_bp
    from .student.routes import student_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(office_bp)
    app.register_blueprint(student_bp)
    
    return app