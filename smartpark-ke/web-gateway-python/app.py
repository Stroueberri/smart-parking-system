"""
SmartPark KE — Intelligent Automated Parking Management System
Web Gateway & API Orchestrator (Python / Flask + SocketIO)
"""

import os
from flask import Flask
from flask_socketio import SocketIO

from models.db_models import ParkingRepository, ParkingSession
from routes.api import api_bp
from routes.views import views_bp
from routes.auth import auth_bp
from sockets.slot_events import register_socket_events
from time_tracker import tracker

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "smartpark-ke-super-secret-key-2026")

    # Initialize Database Schema & Seed Data (Module 8)
    ParkingRepository.init_db()

    # Rehydrate in-memory Time Tracker with any active sessions from DB
    try:
        db = ParkingRepository.get_db()
        active_sessions = db.query(ParkingSession).filter(ParkingSession.status == "ACTIVE").all()
        for s in active_sessions:
            tracker.record_entry(s.session_id, s.vehicle.plate_number, s.slot.slot_label, s.entry_time)
        print(f"[SmartPark Gateway] Rehydrated {len(active_sessions)} active sessions into TimeTracker.")
        db.close()
    except Exception as e:
        print(f"[SmartPark Gateway] Database init note: {e}")

    # Initialize SocketIO for Real-Time Slot Display (Module 3)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    app.extensions["socketio"] = socketio

    # Register Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # Register WebSocket handlers
    register_socket_events(socketio)

    return app, socketio


app, socketio = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("==========================================================")
    print("  SmartPark KE — Python Web Gateway & API Orchestrator    ")
    print(f"  Listening on http://localhost:{port}                     ")
    print("==========================================================")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
