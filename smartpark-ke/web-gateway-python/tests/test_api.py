"""
SmartPark KE — Automated Test Suite
Tests all REST API endpoints, algorithms, and business logic.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Add parent path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models.db_models import ParkingRepository, ParkingSession, Vehicle, ParkingSlot, Tariff
from time_tracker import tracker


@pytest.fixture
def client():
    app, socketio = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_slots(client):
    """Module 3: Test visual slot grid query returns 30 slots across 3 zones."""
    response = client.get("/api/slots")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["totalSlots"] == 30
    assert len(data["zones"]) == 3
    assert data["freeSlotsCount"] > 0


def test_vehicle_entry_and_duplicate_check(client):
    """Module 1 & 2: Test vehicle entry registration and O(1) duplicate prevention."""
    test_plate = "KDA 999Z"

    # 1. First entry should succeed and allocate nearest slot (A1)
    res1 = client.post("/api/entry", json={"plateNumber": test_plate, "vehicleType": "car"})
    assert res1.status_code == 201
    d1 = res1.get_json()
    assert d1["success"] is True
    assert d1["plateNumber"] == test_plate
    assert "allocatedSlot" in d1
    allocated_slot = d1["allocatedSlot"]
    assert allocated_slot["slotLabel"] is not None

    # 2. Duplicate entry check (Module 1): entering same plate while inside must be rejected (409)
    res2 = client.post("/api/entry", json={"plateNumber": test_plate, "vehicleType": "car"})
    assert res2.status_code == 409
    d2 = res2.get_json()
    assert d2["success"] is False
    assert "already inside" in d2["error"]


def test_exit_fee_calculation(client):
    """Module 5: Test exit lookup and fee calculation tariff table."""
    plate = "KDB 888Y"

    # Register entry
    res = client.post("/api/entry", json={"plateNumber": plate, "vehicleType": "car"})
    assert res.status_code == 201
    entry_data = res.get_json()
    session_id = entry_data["sessionId"]

    # Exit lookup immediately (0 mins elapsed -> Free under 30 min grace)
    exit_res = client.get(f"/api/exit/{plate}")
    assert exit_res.status_code == 200
    exit_data = exit_res.get_json()
    assert exit_data["success"] is True
    assert exit_data["plateNumber"] == plate
    assert exit_data["fee"] == 0.0  # Up to 30 mins free

    # Simulate elapsed duration (e.g. 90 minutes -> Tier 2: Kshs 50)
    db = ParkingRepository.get_db()
    session = db.query(ParkingSession).filter(ParkingSession.session_id == session_id).first()
    session.entry_time = datetime.utcnow() - timedelta(minutes=90)
    db.commit()
    db.close()

    exit_res2 = client.get(f"/api/exit/{plate}")
    assert exit_res2.status_code == 200
    d2 = exit_res2.get_json()
    assert d2["fee"] == 50.0  # Up to 2 hours


def test_payment_and_barrier_open(client):
    """Module 6 & 7: Test M-Pesa STK push and webhook confirmation triggering barrier actuator."""
    plate = "KDC 777X"

    # Entry
    res = client.post("/api/entry", json={"plateNumber": plate, "vehicleType": "car"})
    assert res.status_code == 201
    session_id = res.get_json()["sessionId"]

    # STK Push initiation
    stk_res = client.post("/api/payment/stk-push", json={
        "sessionId": session_id,
        "phoneNumber": "254712345678"
    })
    assert stk_res.status_code == 200
    stk_data = stk_res.get_json()
    assert stk_data["success"] is True
    assert "checkoutRequestId" in stk_data

    # Confirm Payment Webhook
    pay_res = client.post("/api/payment/confirm-webhook", json={
        "sessionId": session_id,
        "mpesaReceipt": "QKE1234567",
        "amount": 50.0
    })
    assert pay_res.status_code == 200
    pay_data = pay_res.get_json()
    assert pay_data["success"] is True
    assert pay_data["barrierState"] == "OPEN"

    # Barrier status check (Module 7 LIFO stack)
    b_res = client.get("/api/barrier/status")
    assert b_res.status_code == 200
    b_data = b_res.get_json()
    assert b_data["currentState"] == "OPEN"
    assert b_data["auditStackTop"]["to"] == "OPEN"


def test_reports_revenue_and_occupancy(client):
    """Module 9: Test admin revenue and occupancy reporting endpoints."""
    rev_res = client.get("/api/reports/revenue")
    assert rev_res.status_code == 200
    rev_data = rev_res.get_json()
    assert "totalRevenue" in rev_data
    assert "completedSessions" in rev_data

    occ_res = client.get("/api/reports/occupancy")
    assert occ_res.status_code == 200
    occ_data = occ_res.get_json()
    assert "occupancyRate" in occ_data
    assert len(occ_data["zoneBreakdown"]) == 3


def test_dynamic_tariffs(client):
    """Section 5: Test dynamic tariff addition and querying."""
    res = client.get("/api/tariffs")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["tariffs"]) >= 5

    # Add dynamic tier
    add_res = client.post("/api/tariffs", json={
        "maxMinutes": 720,
        "fee": 400.0,
        "description": "12-hour half-day tariff"
    })
    assert add_res.status_code == 201
