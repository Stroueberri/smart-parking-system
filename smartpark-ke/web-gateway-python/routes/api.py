"""
SmartPark KE — REST API Controller
Section 6: Full REST API Contract Implementation
Covers Modules 1, 2, 3, 4, 5, 6, 7, 8, 9, 11
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func, desc

from models.db_models import (
    ParkingRepository, ParkingSlot, Vehicle, ParkingSession,
    Tariff, Payment, BarrierLog, Zone, Notification
)
from slot_engine_client import slot_client
from billing_client import billing_client
from time_tracker import tracker
from sockets.slot_events import broadcast_slot_update, broadcast_barrier_state

api_bp = Blueprint("api", __name__)


# ---------------------------------------------------------------------------
# Module 3: Live Slot Grid State
# ---------------------------------------------------------------------------
@api_bp.route("/api/slots", methods=["GET"])
def get_slots():
    """
    Returns live visual slot grid matrix.
    Data Structure: 2D Array/Matrix mirroring physical layout (rows x bays).
    """
    db = ParkingRepository.get_db()
    try:
        slots = db.query(ParkingSlot).join(Zone).order_by(ParkingSlot.zone_id, ParkingSlot.row_position, ParkingSlot.col_position).all()
        zones = db.query(Zone).all()

        slot_list = []
        free_count = 0
        occupied_count = 0

        for s in slots:
            is_free = (s.status == "FREE")
            if is_free:
                free_count += 1
            else:
                occupied_count += 1

            # Fetch active vehicle info if occupied
            plate = None
            duration_mins = 0
            if not is_free:
                active_session = db.query(ParkingSession).join(Vehicle).filter(
                    ParkingSession.slot_id == s.slot_id,
                    ParkingSession.status == "ACTIVE"
                ).first()
                if active_session:
                    plate = active_session.vehicle.plate_number
                    duration_mins = tracker.get_elapsed_minutes(plate) or int((datetime.utcnow() - active_session.entry_time).total_seconds() // 60)

            slot_list.append({
                "slotId": s.slot_id,
                "zoneId": s.zone_id,
                "zoneName": s.zone.zone_name,
                "floorLevel": s.zone.floor_level,
                "slotLabel": s.slot_label,
                "distance": float(s.distance_from_entrance),
                "status": s.status,
                "row": s.row_position,
                "col": s.col_position,
                "vehicleType": s.vehicle_type,
                "currentPlate": plate,
                "durationMinutes": duration_mins
            })

        return jsonify({
            "success": True,
            "totalSlots": len(slot_list),
            "freeSlotsCount": free_count,
            "occupiedSlotsCount": occupied_count,
            "slots": slot_list,
            "zones": [{"zoneId": z.zone_id, "name": z.zone_name, "floor": z.floor_level} for z in zones]
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Module 1 & 2: Vehicle Entry & Nearest Slot Allocation
# ---------------------------------------------------------------------------
@api_bp.route("/api/entry", methods=["POST"])
def vehicle_entry():
    """
    Module 1: Vehicle Entry & Registration.
    Algorithm: Hash plate, check duplicate active session O(1), request closest slot from Module 2 C++ engine.
    """
    data = request.get_json(silent=True) or request.form
    raw_plate = data.get("plateNumber", "").strip().upper()
    v_type = data.get("vehicleType", "car").strip().lower()

    if not raw_plate:
        return jsonify({"success": False, "error": "Plate number is required"}), 400

    db = ParkingRepository.get_db()
    try:
        # Module 1: O(1) duplicate entry check via Hash Map / Index
        existing_vehicle = db.query(Vehicle).filter(Vehicle.plate_number == raw_plate).first()
        if existing_vehicle:
            active_session = db.query(ParkingSession).filter(
                ParkingSession.vehicle_id == existing_vehicle.vehicle_id,
                ParkingSession.status == "ACTIVE"
            ).first()
            if active_session:
                return jsonify({
                    "success": False,
                    "error": f"Vehicle {raw_plate} is already inside at slot {active_session.slot.slot_label}!",
                    "slotLabel": active_session.slot.slot_label
                }), 409
        else:
            existing_vehicle = Vehicle(plate_number=raw_plate, vehicle_type=v_type)
            db.add(existing_vehicle)
            db.flush()

        # Module 2: Nearest Slot Allocation Engine (C++ Min-Heap / Dijkstra)
        # Try C++ microservice first; fall back to DB-level nearest free slot
        allocated_slot_info = slot_client.allocate_slot()

        slot = None
        if allocated_slot_info:
            slot = db.query(ParkingSlot).filter(ParkingSlot.slot_id == allocated_slot_info["slotId"]).first()

        if not slot:
            # Query closest free slot by distance
            slot = db.query(ParkingSlot).filter(ParkingSlot.status == "FREE").order_by(ParkingSlot.distance_from_entrance.asc()).first()

        if not slot:
            return jsonify({"success": False, "error": "Parking lot is completely full! No slots available."}), 400

        # Mark slot occupied
        slot.status = "OCCUPIED"

        # Create session record
        entry_now = datetime.utcnow()
        session_record = ParkingSession(
            vehicle_id=existing_vehicle.vehicle_id,
            slot_id=slot.slot_id,
            entry_time=entry_now,
            status="ACTIVE",
            paid=False
        )
        db.add(session_record)
        db.commit()

        # Update Module 4 in-memory Time Tracker (Hash Map + Min-Heap)
        tracker.record_entry(session_record.session_id, raw_plate, slot.slot_label, entry_now)

        # Module 3: Push live WebSocket update to all connected screens
        socketio = current_app.extensions.get("socketio")
        broadcast_slot_update(socketio, {
            "slotId": slot.slot_id,
            "slotLabel": slot.slot_label,
            "status": "OCCUPIED",
            "currentPlate": raw_plate,
            "row": slot.row_position,
            "col": slot.col_position,
            "zoneId": slot.zone_id
        })

        return jsonify({
            "success": True,
            "message": f"Vehicle {raw_plate} registered successfully",
            "sessionId": session_record.session_id,
            "plateNumber": raw_plate,
            "allocatedSlot": {
                "slotId": slot.slot_id,
                "slotLabel": slot.slot_label,
                "zoneId": slot.zone_id,
                "distance": float(slot.distance_from_entrance),
                "row": slot.row_position,
                "col": slot.col_position
            },
            "entryTime": entry_now.strftime("%Y-%m-%d %H:%M:%S")
        }), 201

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Module 5: Exit Lookup & Fee Computation
# ---------------------------------------------------------------------------
@api_bp.route("/api/exit/<plate>", methods=["GET", "POST"])
def vehicle_exit_lookup(plate):
    """
    Module 5: Exit calculation.
    Finds active session for plate, computes duration, queries Java FeeCalculator.
    """
    clean_plate = plate.strip().upper()
    db = ParkingRepository.get_db()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.plate_number == clean_plate).first()
        if not vehicle:
            return jsonify({"success": False, "error": f"Vehicle {clean_plate} not found in system"}), 404

        active_session = db.query(ParkingSession).filter(
            ParkingSession.vehicle_id == vehicle.vehicle_id,
            ParkingSession.status == "ACTIVE"
        ).first()

        if not active_session:
            return jsonify({"success": False, "error": f"No active parking session found for {clean_plate}"}), 404

        now = datetime.utcnow()
        duration_minutes = max(0, int((now - active_session.entry_time).total_seconds() // 60))

        # Query dynamic tariffs from DB
        db_tariffs = db.query(Tariff).order_by(Tariff.max_minutes.asc()).all()

        # Delegate fee computation to Java Billing Microservice (Module 5)
        fee_data = billing_client.calculate_fee(duration_minutes, db_tariffs)

        return jsonify({
            "success": True,
            "sessionId": active_session.session_id,
            "plateNumber": clean_plate,
            "slotLabel": active_session.slot.slot_label,
            "slotId": active_session.slot_id,
            "entryTime": active_session.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "exitTime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "durationMinutes": duration_minutes,
            "formattedDuration": fee_data.get("formattedDuration", f"{duration_minutes} mins"),
            "fee": fee_data.get("fee", 0.0),
            "tariffApplied": fee_data.get("tariffApplied", "Fixed Tariff"),
            "paid": active_session.paid
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Module 6: M-Pesa STK Push Dispatch
# ---------------------------------------------------------------------------
@api_bp.route("/api/payment/stk-push", methods=["POST"])
def initiate_stk_push():
    """
    Module 6: Proxies STK Push to Java Spring Boot Payment Service.
    """
    data = request.get_json(silent=True) or request.form
    session_id = data.get("sessionId")
    phone_number = data.get("phoneNumber", "").strip()

    if not session_id or not phone_number:
        return jsonify({"success": False, "error": "sessionId and phoneNumber are required"}), 400

    db = ParkingRepository.get_db()
    try:
        session_record = db.query(ParkingSession).filter(ParkingSession.session_id == int(session_id)).first()
        if not session_record:
            return jsonify({"success": False, "error": "Session not found"}), 404

        # Compute fee
        duration = max(0, int((datetime.utcnow() - session_record.entry_time).total_seconds() // 60))
        tariffs = db.query(Tariff).order_by(Tariff.max_minutes.asc()).all()
        fee_info = billing_client.calculate_fee(duration, tariffs)
        amount = fee_info.get("fee", 0.0)

        # Dispatch STK Push via Java Service (Module 6)
        plate = session_record.vehicle.plate_number
        stk_res = billing_client.initiate_stk_push(session_record.session_id, plate, phone_number, amount)

        # Save payment record in DB
        payment = Payment(
            session_id=session_record.session_id,
            phone_number=phone_number,
            amount=amount,
            mpesa_checkout_request_id=stk_res.get("checkoutRequestId"),
            result_code=-1
        )
        db.add(payment)
        db.commit()

        return jsonify({
            "success": stk_res.get("success", True),
            "checkoutRequestId": stk_res.get("checkoutRequestId"),
            "merchantRequestId": stk_res.get("merchantRequestId"),
            "amount": amount,
            "message": stk_res.get("customerMessage", "STK push initiated")
        })
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Module 6 & 7: Payment Confirmation Webhook & Barrier Actuator Trigger
# ---------------------------------------------------------------------------
@api_bp.route("/api/payment/confirm-webhook", methods=["POST"])
def payment_confirm_webhook():
    """
    Webhook called when M-Pesa confirms payment.
    Marks session paid, frees slot in C++ engine and DB, triggers barrier actuator.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("sessionId")
    receipt = data.get("mpesaReceipt")
    amount = data.get("amount", 0.0)

    if not session_id:
        return jsonify({"error": "Missing sessionId"}), 400

    db = ParkingRepository.get_db()
    try:
        session_record = db.query(ParkingSession).filter(ParkingSession.session_id == int(session_id)).first()
        if not session_record:
            return jsonify({"error": "Session not found"}), 404

        now = datetime.utcnow()
        session_record.paid = True
        session_record.status = "COMPLETED"
        session_record.exit_time = now
        session_record.duration_minutes = max(0, int((now - session_record.entry_time).total_seconds() // 60))
        session_record.fee_charged = float(amount)

        # Update payment record
        payment = db.query(Payment).filter(Payment.session_id == session_record.session_id).first()
        if payment:
            payment.result_code = 0
            payment.mpesa_receipt_number = receipt or f"NLM{now.strftime('%H%M%S')}"
            payment.payment_time = now

        # Free the slot in database
        slot = session_record.slot
        slot.status = "FREE"

        # Module 2: Free slot re-insertion into C++ Min-Heap & Doubly Linked List
        slot_client.release_slot(slot.slot_id)

        # Module 4: Remove from active time tracking
        tracker.record_exit(session_record.vehicle.plate_number)

        # Module 7: Trigger barrier FSM to OPEN
        barrier_res = slot_client.trigger_barrier("PAYMENT_CONFIRMED", session_record.session_id)

        # Audit log in DB
        blog = BarrierLog(
            session_id=session_record.session_id,
            barrier_direction="EXIT",
            state="OPEN",
            trigger_source="AUTO_PAYMENT"
        )
        db.add(blog)

        # Module 11: Queue notification receipt in DB
        notif = Notification(
            session_id=session_record.session_id,
            channel="sms",
            recipient=payment.phone_number if payment else "254700000000",
            content=f"SmartPark KE: Kshs {amount} received for {session_record.vehicle.plate_number}. Exit barrier opened.",
            status="SENT"
        )
        db.add(notif)
        db.commit()

        # Module 3: Broadcast live slot update + barrier state to WebSocket clients
        socketio = current_app.extensions.get("socketio")
        broadcast_slot_update(socketio, {
            "slotId": slot.slot_id,
            "slotLabel": slot.slot_label,
            "status": "FREE",
            "currentPlate": None,
            "row": slot.row_position,
            "col": slot.col_position,
            "zoneId": slot.zone_id
        })
        broadcast_barrier_state(socketio, {
            "state": "OPEN",
            "sessionId": session_record.session_id,
            "plateNumber": session_record.vehicle.plate_number,
            "lastTransition": barrier_res.get("lastTransition")
        })

        return jsonify({
            "success": True,
            "message": "Payment verified and barrier opened",
            "barrierState": barrier_res.get("currentState", "OPEN"),
            "mpesaReceipt": payment.mpesa_receipt_number if payment else receipt
        })
    finally:
        db.close()


@api_bp.route("/api/barrier/open/<int:session_id>", methods=["POST"])
def force_open_barrier(session_id):
    """
    Module 7: Force-open barrier endpoint after confirmed payment.
    """
    res = slot_client.trigger_barrier("FORCE_OPEN", session_id)
    socketio = current_app.extensions.get("socketio")
    broadcast_barrier_state(socketio, {"state": "OPEN", "sessionId": session_id, "trigger": "FORCE_OPEN"})
    return jsonify(res)


@api_bp.route("/api/barrier/sensor-cleared", methods=["POST"])
def barrier_sensor_cleared():
    """
    Module 7: Vehicle passage sensor tripped -> transitions gate to CLOSING -> CLOSED.
    """
    res = slot_client.trigger_barrier("SENSOR_CLEARED", 0)
    socketio = current_app.extensions.get("socketio")
    broadcast_barrier_state(socketio, {"state": "CLOSED", "trigger": "SENSOR_CLEARED"})
    return jsonify(res)


@api_bp.route("/api/barrier/status", methods=["GET"])
def get_barrier_status():
    """
    Module 7: Returns current barrier FSM state and LIFO audit log stack.
    """
    return jsonify(slot_client.get_barrier_status())


# ---------------------------------------------------------------------------
# Module 9: Admin Analytics & Reports
# ---------------------------------------------------------------------------
@api_bp.route("/api/reports/revenue", methods=["GET"])
def get_revenue_report():
    """
    Module 9: Admin revenue report (daily, weekly, total, by vehicle type).
    Backed by database B-Tree index on entry/exit timestamps.
    """
    db = ParkingRepository.get_db()
    try:
        total_revenue = db.query(func.sum(ParkingSession.fee_charged)).filter(ParkingSession.paid == True).scalar() or 0.0
        completed_sessions = db.query(func.count(ParkingSession.session_id)).filter(ParkingSession.paid == True).scalar() or 0
        active_sessions_count = db.query(func.count(ParkingSession.session_id)).filter(ParkingSession.status == "ACTIVE").scalar() or 0

        # Recent 7 completed sessions for chart
        recent = db.query(ParkingSession).filter(ParkingSession.paid == True).order_by(ParkingSession.exit_time.desc()).limit(10).all()

        recent_data = [{
            "sessionId": s.session_id,
            "plate": s.vehicle.plate_number,
            "amount": float(s.fee_charged),
            "exitTime": s.exit_time.strftime("%Y-%m-%d %H:%M:%S") if s.exit_time else ""
        } for s in recent]

        return jsonify({
            "totalRevenue": float(total_revenue),
            "completedSessions": completed_sessions,
            "activeSessions": active_sessions_count,
            "currency": "Kshs",
            "recentTransactions": recent_data
        })
    finally:
        db.close()


@api_bp.route("/api/reports/occupancy", methods=["GET"])
def get_occupancy_report():
    """
    Module 9: Real-time and historical occupancy metrics.
    """
    db = ParkingRepository.get_db()
    try:
        total = db.query(ParkingSlot).count()
        occupied = db.query(ParkingSlot).filter(ParkingSlot.status == "OCCUPIED").count()
        free = total - occupied
        occupancy_rate = (occupied / total * 100.0) if total > 0 else 0.0

        # Occupancy by zone
        zones = db.query(Zone).all()
        zone_stats = []
        for z in zones:
            z_total = db.query(ParkingSlot).filter(ParkingSlot.zone_id == z.zone_id).count()
            z_occ = db.query(ParkingSlot).filter(ParkingSlot.zone_id == z.zone_id, ParkingSlot.status == "OCCUPIED").count()
            zone_stats.append({
                "zoneId": z.zone_id,
                "name": z.zone_name,
                "total": z_total,
                "occupied": z_occ,
                "free": z_total - z_occ,
                "rate": round((z_occ / z_total * 100.0) if z_total > 0 else 0, 1)
            })

        return jsonify({
            "totalSlots": total,
            "occupiedSlots": occupied,
            "freeSlots": free,
            "occupancyRate": round(occupancy_rate, 1),
            "zoneBreakdown": zone_stats
        })
    finally:
        db.close()


@api_bp.route("/api/reports/overstay", methods=["GET"])
def get_overstay_report():
    """
    Module 4 & 9: Overstay alerts using Module 4 Min-Heap.
    """
    threshold = request.args.get("threshold", 360, type=int)
    overstays = tracker.get_overstay_vehicles(threshold)
    longest = tracker.get_longest_parked_vehicles(limit=10)
    return jsonify({
        "thresholdMinutes": threshold,
        "overstayVehicles": overstays,
        "longestParked": longest
    })


# ---------------------------------------------------------------------------
# Dynamic Tariffs Management (Section 5 dynamic requirement)
# ---------------------------------------------------------------------------
@api_bp.route("/api/tariffs", methods=["GET", "POST"])
def manage_tariffs():
    db = ParkingRepository.get_db()
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or request.form
            max_mins = int(data.get("maxMinutes", 60))
            fee = float(data.get("fee", 50.0))
            desc_text = data.get("description", f"Up to {max_mins} mins")

            tariff = Tariff(max_minutes=max_mins, fee=fee, description=desc_text)
            db.add(tariff)
            db.commit()
            return jsonify({"success": True, "message": "Tariff created successfully"}), 201

        tariffs = db.query(Tariff).order_by(Tariff.max_minutes.asc()).all()
        return jsonify({
            "tariffs": [{
                "tariffId": t.tariff_id,
                "maxMinutes": t.max_minutes,
                "fee": float(t.fee),
                "description": t.description
            } for t in tariffs]
        })
    finally:
        db.close()
