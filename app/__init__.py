from flask import Flask 
from .extensions import db
from pathlib import Path
from flask_socketio import SocketIO
from flask_login import LoginManager, current_user
from flask import g

socketio = SocketIO()
login_manager = LoginManager() 

def create_app():
    root_path = Path(__file__).parent.parent

    app = Flask(__name__
                , template_folder=str(root_path / "templates"),
                static_folder=str(root_path / "static")
                )
    app.config.from_object('config.Config')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' 
    
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

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Make current_user available in all templates
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    socketio.init_app(app)
    
    return app