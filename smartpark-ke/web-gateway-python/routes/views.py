"""
SmartPark KE — Web Views Controller
Section 7: Web Interface Views
"""

from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required, role_required

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def driver_display():
    """
    View 1: Public Driver Display (Entrance Kiosk Screen).
    Visual color-coded grid: green (free), red (occupied), yellow (reserved).
    Free slots counter, nearest slot indicator, vehicle entry simulator.
    """
    return render_template("driver_display.html", title="SmartPark KE — Driver Entrance Display")


@views_bp.route("/attendant")
def attendant_kiosk():
    """
    View 2: Attendant / Exit Kiosk.
    Plate lookup -> duration & fee computation -> M-Pesa STK push -> barrier animation.
    """
    return render_template("attendant_kiosk.html", title="SmartPark KE — Attendant Checkout Kiosk")


@views_bp.route("/admin")
def admin_dashboard():
    """
    View 3: Admin Analytics & Management Dashboard.
    Chart.js revenue analytics, occupancy metrics, overstay alerts, barrier state audit, dynamic tariffs.
    """
    return render_template("admin_dashboard.html", title="SmartPark KE — Admin Analytics Dashboard")


@views_bp.route("/login")
def login_page():
    return render_template("login.html", title="SmartPark KE — Portal Login")
