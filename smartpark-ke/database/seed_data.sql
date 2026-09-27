-- ============================================================================
-- SmartPark KE — Seed Data (Tariffs, Zones, Slots, Default Users)
-- ============================================================================

-- 1. Insert Zones
INSERT INTO zones (zone_id, zone_name, floor_level) VALUES
(1, 'Ground Floor - Zone A (Near Entrance)', 0),
(2, 'Ground Floor - Zone B (West Wing)', 0),
(3, 'Upper Floor - Zone C (Rooftop Deck)', 1)
ON CONFLICT (zone_id) DO NOTHING;

-- 2. Insert Fixed Tariffs (Dynamic Tariff Table per Section 1.8)
-- Up to 30 min: Free
-- Up to 2 hours (120 min): 50 Kshs
-- Up to 4 hours (240 min): 100 Kshs
-- Up to 6 hours (360 min): 300 Kshs
-- Over 6 hours (up to 1440 min/24h): 500 Kshs
INSERT INTO tariffs (tariff_id, max_minutes, fee, description) VALUES
(1, 30, 0.00, 'Up to 30 minutes (Grace period / Free)'),
(2, 120, 50.00, 'Up to 2 hours (Short stay)'),
(3, 240, 100.00, 'Up to 4 hours (Standard stay)'),
(4, 360, 300.00, 'Up to 6 hours (Extended stay)'),
(5, 1440, 500.00, 'Over 6 hours (Full day)')
ON CONFLICT (tariff_id) DO NOTHING;

-- 3. Insert Parking Slots (Layout with physical row/col and distance from entrance)
-- Zone A (10 slots, closest to entrance)
INSERT INTO parking_slots (slot_id, zone_id, slot_label, distance_from_entrance, status, row_position, col_position, vehicle_type) VALUES
(1, 1, 'A1', 5.0, 'FREE', 1, 1, 'car'),
(2, 1, 'A2', 8.5, 'FREE', 1, 2, 'car'),
(3, 1, 'A3', 12.0, 'FREE', 1, 3, 'car'),
(4, 1, 'A4', 15.5, 'FREE', 1, 4, 'car'),
(5, 1, 'A5', 19.0, 'FREE', 1, 5, 'car'),
(6, 1, 'A6', 7.5, 'FREE', 2, 1, 'car'),
(7, 1, 'A7', 10.5, 'FREE', 2, 2, 'car'),
(8, 1, 'A8', 14.0, 'FREE', 2, 3, 'car'),
(9, 1, 'A9', 17.5, 'FREE', 2, 4, 'car'),
(10, 1, 'A10', 21.0, 'FREE', 2, 5, 'car'),

-- Zone B (10 slots, medium distance)
(11, 2, 'B1', 25.0, 'FREE', 1, 1, 'car'),
(12, 2, 'B2', 28.5, 'FREE', 1, 2, 'car'),
(13, 2, 'B3', 32.0, 'FREE', 1, 3, 'car'),
(14, 2, 'B4', 35.5, 'FREE', 1, 4, 'car'),
(15, 2, 'B5', 39.0, 'FREE', 1, 5, 'car'),
(16, 2, 'B6', 27.0, 'FREE', 2, 1, 'car'),
(17, 2, 'B7', 30.5, 'FREE', 2, 2, 'car'),
(18, 2, 'B8', 34.0, 'FREE', 2, 3, 'car'),
(19, 2, 'B9', 37.5, 'FREE', 2, 4, 'car'),
(20, 2, 'B10', 41.0, 'FREE', 2, 5, 'car'),

-- Zone C (10 slots, upper deck via ramp)
(21, 3, 'C1', 50.0, 'FREE', 1, 1, 'car'),
(22, 3, 'C2', 53.5, 'FREE', 1, 2, 'car'),
(23, 3, 'C3', 57.0, 'FREE', 1, 3, 'car'),
(24, 3, 'C4', 60.5, 'FREE', 1, 4, 'car'),
(25, 3, 'C5', 64.0, 'FREE', 1, 5, 'car'),
(26, 3, 'C6', 52.0, 'FREE', 2, 1, 'car'),
(27, 3, 'C7', 55.5, 'FREE', 2, 2, 'car'),
(28, 3, 'C8', 59.0, 'FREE', 2, 3, 'car'),
(29, 3, 'C9', 62.5, 'FREE', 2, 4, 'car'),
(30, 3, 'C10', 66.0, 'FREE', 2, 5, 'car')
ON CONFLICT (slot_id) DO NOTHING;

-- 4. Insert Default Users (Admin, Attendant, Driver Kiosk)
-- Password for all default accounts is 'SmartPark2026!'
-- werkzeug generate_password_hash('SmartPark2026!')
INSERT INTO users (user_id, username, password_hash, role, full_name) VALUES
(1, 'admin', 'scrypt:32768:8:1$uH9N1Y1Q8uYk7Q7z$e93ff58dcb3e956bc5f8b9dfbf40c946e4b98fa39535aa69352e69748b59ee7f5ee0eeceba05273f00ca09fc8467d0cf0c07ffdf5a86dca50a228f2382f6f1a8', 'admin', 'System Administrator'),
(2, 'attendant', 'scrypt:32768:8:1$uH9N1Y1Q8uYk7Q7z$e93ff58dcb3e956bc5f8b9dfbf40c946e4b98fa39535aa69352e69748b59ee7f5ee0eeceba05273f00ca09fc8467d0cf0c07ffdf5a86dca50a228f2382f6f1a8', 'attendant', 'Duty Gate Attendant'),
(3, 'kiosk', 'scrypt:32768:8:1$uH9N1Y1Q8uYk7Q7z$e93ff58dcb3e956bc5f8b9dfbf40c946e4b98fa39535aa69352e69748b59ee7f5ee0eeceba05273f00ca09fc8467d0cf0c07ffdf5a86dca50a228f2382f6f1a8', 'driver-kiosk', 'Driver Self-Service Kiosk')
ON CONFLICT (user_id) DO NOTHING;
