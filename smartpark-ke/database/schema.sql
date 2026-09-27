-- ============================================================================
-- SmartPark KE — Dynamic Database Schema
-- Compatible with PostgreSQL, MySQL 8.0+, and SQLite (via SQLAlchemy)
-- ============================================================================

-- Drop existing tables in reverse dependency order if resetting
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS barrier_logs;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS parking_sessions;
DROP TABLE IF EXISTS tariffs;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS parking_slots;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS users;

-- 1. Zones Table (Dynamic Multi-Floor / Multi-Area Configuration)
CREATE TABLE zones (
    zone_id SERIAL PRIMARY KEY,
    zone_name VARCHAR(50) NOT NULL UNIQUE,
    floor_level INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Parking Slots Table (Physical Coordinate Mapping & Current Status)
CREATE TABLE parking_slots (
    slot_id SERIAL PRIMARY KEY,
    zone_id INT NOT NULL REFERENCES zones(zone_id) ON DELETE CASCADE,
    slot_label VARCHAR(10) NOT NULL UNIQUE,            -- e.g. "A1", "A2", "B1"
    distance_from_entrance DECIMAL(6,2) NOT NULL,      -- in meters
    status VARCHAR(15) DEFAULT 'FREE',                 -- FREE / OCCUPIED / RESERVED / MAINTENANCE
    row_position INT NOT NULL,                         -- row coordinate in zone grid
    col_position INT NOT NULL,                         -- column coordinate in zone grid
    vehicle_type VARCHAR(20) DEFAULT 'car',            -- car / motorbike / truck / ev
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parking_slots_status ON parking_slots(status);
CREATE INDEX idx_parking_slots_zone ON parking_slots(zone_id);

-- 3. Vehicles Registry Table
CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    plate_number VARCHAR(15) UNIQUE NOT NULL,          -- e.g. "KDA 123A"
    vehicle_type VARCHAR(20) DEFAULT 'car',            -- car, motorbike, truck, van
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vehicles_plate ON vehicles(plate_number);

-- 4. Parking Sessions Table (Active & Historical Lifecycle)
CREATE TABLE parking_sessions (
    session_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL REFERENCES vehicles(vehicle_id) ON DELETE RESTRICT,
    slot_id INT NOT NULL REFERENCES parking_slots(slot_id) ON DELETE RESTRICT,
    entry_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    duration_minutes INT DEFAULT 0,
    fee_charged DECIMAL(8,2) DEFAULT 0.00,
    paid BOOLEAN DEFAULT FALSE,
    status VARCHAR(15) DEFAULT 'ACTIVE'                -- ACTIVE / COMPLETED / CANCELLED
);

-- B-Tree indexes for high-speed range queries on timestamps & active lookup
CREATE INDEX idx_sessions_entry_time ON parking_sessions(entry_time);
CREATE INDEX idx_sessions_exit_time ON parking_sessions(exit_time);
CREATE INDEX idx_sessions_status ON parking_sessions(status);
CREATE INDEX idx_sessions_vehicle_status ON parking_sessions(vehicle_id, status);

-- 5. Tariffs Table (Dynamic, Data-Driven Fixed Tariff Table)
CREATE TABLE tariffs (
    tariff_id SERIAL PRIMARY KEY,
    max_minutes INT NOT NULL,                          -- upper bound minutes (e.g. 30, 120, 240, 360, 1440)
    fee DECIMAL(8,2) NOT NULL,                         -- Kshs amount (0, 50, 100, 300, 500)
    effective_from DATE DEFAULT CURRENT_DATE,
    description VARCHAR(100)
);

CREATE INDEX idx_tariffs_max_minutes ON tariffs(max_minutes);

-- 6. Payments Table (Safaricom Daraja M-Pesa STK Push Records)
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES parking_sessions(session_id) ON DELETE RESTRICT,
    phone_number VARCHAR(15) NOT NULL,                 -- e.g. "254712345678"
    amount DECIMAL(8,2) NOT NULL,
    mpesa_checkout_request_id VARCHAR(60) UNIQUE,
    mpesa_receipt_number VARCHAR(30) UNIQUE,
    result_code INT DEFAULT -1,                        -- 0 = success, other = pending/failed
    result_desc VARCHAR(255),
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_session ON payments(session_id);
CREATE INDEX idx_payments_checkout_req ON payments(mpesa_checkout_request_id);

-- 7. Barrier Logs Table (FSM State Transition Audit Trail)
CREATE TABLE barrier_logs (
    log_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES parking_sessions(session_id) ON DELETE SET NULL,
    barrier_direction VARCHAR(10) DEFAULT 'EXIT',      -- ENTRY / EXIT
    state VARCHAR(15) NOT NULL,                        -- CLOSED / OPENING / OPEN / CLOSING
    trigger_source VARCHAR(30) DEFAULT 'AUTO_PAYMENT', -- AUTO_PAYMENT / SENSOR_TIMEOUT / MANUAL_OVERRIDE
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_barrier_logs_time ON barrier_logs(changed_at);

-- 8. Users Table (Role-Based Access Control)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(15) NOT NULL DEFAULT 'attendant',     -- admin / attendant / driver-kiosk
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Notifications Table (Outbound SMS / Email Receipts Queue)
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES parking_sessions(session_id) ON DELETE SET NULL,
    channel VARCHAR(10) DEFAULT 'sms',                 -- sms / email
    recipient VARCHAR(100) NOT NULL,                   -- phone number or email
    content TEXT NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(15) DEFAULT 'PENDING'               -- PENDING / SENT / FAILED
);

CREATE INDEX idx_notifications_status ON notifications(status);
