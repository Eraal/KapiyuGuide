from app.extensions import socketio

def init_app():
    """Initialize all WebSocket modules"""
    from app.websockets.admin_sockets import init_socketio as init_admin_socketio
    
    from app.websockets.student_sockets import init_socketio as init_student_socketio
    from app.websockets.office_sockets import init_socketio as init_office_socketio
    
    # Initialize socketio handlers
    init_admin_socketio()
    init_student_socketio()
    init_office_socketio()