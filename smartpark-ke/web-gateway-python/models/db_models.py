"""
SmartPark KE — Database Models & Repository Pattern Layer
Module 8: Database Management Module
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///smartpark.db")

# Handle PostgreSQL prefix if postgres:// is used
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


class Zone(Base):
    __tablename__ = "zones"

    zone_id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(50), unique=True, nullable=False)
    floor_level = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    slots = relationship("ParkingSlot", back_populates="zone", cascade="all, delete-orphan")


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    slot_id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.zone_id", ondelete="CASCADE"), nullable=False, index=True)
    slot_label = Column(String(10), unique=True, nullable=False)
    distance_from_entrance = Column(Float, nullable=False)
    status = Column(String(15), default="FREE", index=True)  # FREE, OCCUPIED, RESERVED, MAINTENANCE
    row_position = Column(Integer, nullable=False)
    col_position = Column(Integer, nullable=False)
    vehicle_type = Column(String(20), default="car")
    created_at = Column(DateTime, default=datetime.utcnow)

    zone = relationship("Zone", back_populates="slots")
    sessions = relationship("ParkingSession", back_populates="slot")


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(15), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(20), default="car")
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ParkingSession", back_populates="vehicle")


class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("parking_slots.slot_id"), nullable=False, index=True)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    exit_time = Column(DateTime, nullable=True, index=True)
    duration_minutes = Column(Integer, default=0)
    fee_charged = Column(Float, default=0.0)
    paid = Column(Boolean, default=False)
    status = Column(String(15), default="ACTIVE", index=True)  # ACTIVE, COMPLETED, CANCELLED

    vehicle = relationship("Vehicle", back_populates="sessions")
    slot = relationship("ParkingSlot", back_populates="sessions")
    payments = relationship("Payment", back_populates="session")
    barrier_logs = relationship("BarrierLog", back_populates="session")


class Tariff(Base):
    __tablename__ = "tariffs"

    tariff_id = Column(Integer, primary_key=True, index=True)
    max_minutes = Column(Integer, nullable=False, index=True)
    fee = Column(Float, nullable=False)
    effective_from = Column(DateTime, default=datetime.utcnow)
    description = Column(String(100))


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("parking_sessions.session_id"), nullable=False, index=True)
    phone_number = Column(String(15), nullable=False)
    amount = Column(Float, nullable=False)
    mpesa_checkout_request_id = Column(String(60), unique=True, index=True)
    mpesa_receipt_number = Column(String(30), unique=True, nullable=True)
    result_code = Column(Integer, default=-1)
    result_desc = Column(String(255), nullable=True)
    payment_time = Column(DateTime, default=datetime.utcnow)

    session = relationship("ParkingSession", back_populates="payments")


class BarrierLog(Base):
    __tablename__ = "barrier_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("parking_sessions.session_id"), nullable=True)
    barrier_direction = Column(String(10), default="EXIT")
    state = Column(String(15), nullable=False)  # CLOSED, OPENING, OPEN, CLOSING
    trigger_source = Column(String(30), default="AUTO_PAYMENT")
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)

    session = relationship("ParkingSession", back_populates="barrier_logs")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(15), default="attendant")  # admin, attendant, driver-kiosk
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("parking_sessions.session_id"), nullable=True)
    channel = Column(String(10), default="sms")
    recipient = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(15), default="SENT")  # PENDING, SENT, FAILED


# ============================================================================
# Repository Pattern Implementation (Data Access Layer - Module 8)
# All writes and queries go through this layer
# ============================================================================

class ParkingRepository:
    """Central data-access repository guaranteeing data integrity."""

    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise

    @staticmethod
    def init_db():
        """Creates tables and populates seed data if empty."""
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            # Seed zones if empty
            if db.query(Zone).count() == 0:
                z1 = Zone(zone_id=1, zone_name="Ground Floor - Zone A (Near Entrance)", floor_level=0)
                z2 = Zone(zone_id=2, zone_name="Ground Floor - Zone B (West Wing)", floor_level=0)
                z3 = Zone(zone_id=3, zone_name="Upper Floor - Zone C (Rooftop Deck)", floor_level=1)
                db.add_all([z1, z2, z3])
                db.commit()

            # Seed tariffs if empty
            if db.query(Tariff).count() == 0:
                t1 = Tariff(tariff_id=1, max_minutes=30, fee=0.0, description="Up to 30 minutes (Free)")
                t2 = Tariff(tariff_id=2, max_minutes=120, fee=50.0, description="Up to 2 hours (Kshs 50)")
                t3 = Tariff(tariff_id=3, max_minutes=240, fee=100.0, description="Up to 4 hours (Kshs 100)")
                t4 = Tariff(tariff_id=4, max_minutes=360, fee=300.0, description="Up to 6 hours (Kshs 300)")
                t5 = Tariff(tariff_id=5, max_minutes=1440, fee=500.0, description="Over 6 hours (Kshs 500)")
                db.add_all([t1, t2, t3, t4, t5])
                db.commit()

            # Seed slots if empty
            if db.query(ParkingSlot).count() == 0:
                slots = []
                # Zone A
                for i in range(1, 11):
                    dist = 5.0 + (i - 1) * 3.5
                    row = 1 if i <= 5 else 2
                    col = ((i - 1) % 5) + 1
                    slots.append(ParkingSlot(slot_id=i, zone_id=1, slot_label=f"A{i}", distance_from_entrance=dist, status="FREE", row_position=row, col_position=col))
                # Zone B
                for i in range(1, 11):
                    slot_id = 10 + i
                    dist = 25.0 + (i - 1) * 3.5
                    row = 1 if i <= 5 else 2
                    col = ((i - 1) % 5) + 1
                    slots.append(ParkingSlot(slot_id=slot_id, zone_id=2, slot_label=f"B{i}", distance_from_entrance=dist, status="FREE", row_position=row, col_position=col))
                # Zone C
                for i in range(1, 11):
                    slot_id = 20 + i
                    dist = 50.0 + (i - 1) * 3.5
                    row = 1 if i <= 5 else 2
                    col = ((i - 1) % 5) + 1
                    slots.append(ParkingSlot(slot_id=slot_id, zone_id=3, slot_label=f"C{i}", distance_from_entrance=dist, status="FREE", row_position=row, col_position=col))
                db.add_all(slots)
                db.commit()

            # Seed users if empty
            from werkzeug.security import generate_password_hash
            if db.query(User).count() == 0:
                pw_hash = generate_password_hash("SmartPark2026!")
                u1 = User(user_id=1, username="admin", password_hash=pw_hash, role="admin", full_name="System Administrator")
                u2 = User(user_id=2, username="attendant", password_hash=pw_hash, role="attendant", full_name="Gate Attendant")
                u3 = User(user_id=3, username="kiosk", password_hash=pw_hash, role="driver-kiosk", full_name="Driver Self Kiosk")
                db.add_all([u1, u2, u3])
                db.commit()

        finally:
            db.close()
