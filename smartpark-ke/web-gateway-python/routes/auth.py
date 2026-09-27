"""
SmartPark KE — Authentication & Role-Based Access Control
Module 10: Authentication & Security Module
"""

from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from models.db_models import ParkingRepository, User

auth_bp = Blueprint("auth", __name__)

# In-memory Hash Map for fast active session and role lookup: session_id -> user_dict
ACTIVE_SESSIONS = {}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized. Login required"}), 401
            return redirect(url_for("views.login_page"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Unauthorized"}), 401
                return redirect(url_for("views.login_page"))
            user_role = session.get("role", "guest")
            if user_role not in allowed_roles:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Forbidden: Insufficient privileges"}), 403
                return "Access Denied: You do not have permission to view this page", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route("/api/auth/login", methods=["POST"])
def login_api():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = ParkingRepository.get_db()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"success": False, "error": "Invalid username or password"}), 401

        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role
        session["full_name"] = user.full_name or user.username

        ACTIVE_SESSIONS[user.user_id] = {
            "username": user.username,
            "role": user.role
        }

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "userId": user.user_id,
                "username": user.username,
                "role": user.role,
                "fullName": user.full_name
            }
        })
    finally:
        db.close()


@auth_bp.route("/api/auth/logout", methods=["POST", "GET"])
def logout_api():
    uid = session.pop("user_id", None)
    session.pop("username", None)
    session.pop("role", None)
    session.pop("full_name", None)
    if uid in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS.pop(uid, None)
    return redirect(url_for("views.login_page"))
