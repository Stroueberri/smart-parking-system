"""
SmartPark KE — WebSocket Event Handler
Module 3: Real-Time Visual Slot Display
Pushes live slot state diffs and barrier events over WebSocket (Flask-SocketIO).
"""

from flask_socketio import emit, join_room

def register_socket_events(socketio):

    @socketio.on('connect')
    def handle_connect():
        emit('connection_status', {'status': 'connected', 'message': 'Subscribed to live slot events'})

    @socketio.on('join_display')
    def handle_join_display():
        join_room('slot_observers')
        emit('room_joined', {'room': 'slot_observers'})

    @socketio.on('ping_server')
    def handle_ping():
        emit('pong_client', {'server_time': 'UP'})


def broadcast_slot_update(socketio, slot_data: dict):
    """
    Broadcasts state diff for an individual parking bay to all connected browsers.
    Avoids expensive full-page polling (O(1) client DOM update).
    """
    if socketio:
        socketio.emit('slot_state_changed', slot_data, namespace='/')


def broadcast_barrier_state(socketio, barrier_data: dict):
    """
    Broadcasts barrier actuator transition events (OPEN / CLOSED / OPENING).
    """
    if socketio:
        socketio.emit('barrier_state_changed', barrier_data, namespace='/')
