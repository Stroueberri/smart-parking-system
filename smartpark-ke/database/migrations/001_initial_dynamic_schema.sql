-- Migration 001: Initial dynamic schema creation
-- SmartPark KE Database Initial Migration

-- Includes zones, parking_slots, vehicles, parking_sessions, tariffs, payments, barrier_logs, users, notifications
-- Matches schema.sql definitions
\i database/schema.sql;
\i database/seed_data.sql;
