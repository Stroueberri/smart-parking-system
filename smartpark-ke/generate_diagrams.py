"""
SmartPark KE — High-Resolution Diagram Generator
Generates architecture_diagram.png and ERD_diagram.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "docs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0f172a')

    # Title
    ax.text(7, 9.5, "SmartPark KE — Polyglot Microservices Architecture", 
            fontsize=18, fontweight='bold', color='#f8fafc', ha='center', va='center')
    ax.text(7, 9.15, "Intelligent Automated Parking Management System (Kenya)", 
            fontsize=12, color='#94a3b8', ha='center', va='center')

    # Box 1: Browser UI
    ui_box = patches.FancyBboxPatch((4.5, 7.5), 5.0, 1.2, boxstyle="round,pad=0.2", 
                                    fc='#1e293b', ec='#3b82f6', lw=2)
    ax.add_patch(ui_box)
    ax.text(7, 8.3, "BROWSER CLIENTS (Driver Kiosk / Attendant / Admin)", 
            fontsize=11, fontweight='bold', color='#60a5fa', ha='center')
    ax.text(7, 7.8, "HTML5 + CSS3 + Vanilla JS + Chart.js + Socket.IO\nReal-Time 2D Bay Visualizer & Interactive Gate Simulation", 
            fontsize=9, color='#cbd5e1', ha='center')

    # Box 2: Python Web Gateway
    py_box = patches.FancyBboxPatch((3.5, 4.8), 7.0, 1.8, boxstyle="round,pad=0.2", 
                                    fc='#1e293b', ec='#10b981', lw=2)
    ax.add_patch(py_box)
    ax.text(7, 6.2, "PYTHON API GATEWAY & ORCHESTRATOR (Flask + SocketIO)", 
            fontsize=12, fontweight='bold', color='#34d399', ha='center')
    ax.text(7, 5.5, "• Serves Driver / Attendant / Admin Web Interfaces\n• Vehicle Entry / Exit Endpoints & Duplicate Detection (Hash Map)\n• In-Memory Active Time Tracking & Overstay Min-Heap\n• WebSocket Live Slot-Diff & Barrier-State Broadcaster", 
            fontsize=9, color='#cbd5e1', ha='center')

    # Box 3: C++ Slot Engine
    cpp_box = patches.FancyBboxPatch((0.5, 1.8), 5.5, 2.0, boxstyle="round,pad=0.2", 
                                     fc='#1e293b', ec='#f59e0b', lw=2)
    ax.add_patch(cpp_box)
    ax.text(3.25, 3.4, "C++ SLOT ALLOCATION & BARRIER ENGINE", 
            fontsize=11, fontweight='bold', color='#fbbf24', ha='center')
    ax.text(3.25, 2.55, "• High-Performance Slot Min-Heap: O(log n)\n• Multi-Floor Lot Graph + Dijkstra Algorithm: O((V+E)log V)\n• Physical Row Doubly Linked Lists: O(1) status & neighbor sync\n• Barrier Finite State Machine (CLOSED/OPENING/OPEN/CLOSING)\n• LIFO Stack Audit Trail for Safety Transitions: O(1)", 
            fontsize=8.5, color='#cbd5e1', ha='center')

    # Box 4: Java Billing Service
    java_box = patches.FancyBboxPatch((8.0, 1.8), 5.5, 2.0, boxstyle="round,pad=0.2", 
                                      fc='#1e293b', ec='#ec4899', lw=2)
    ax.add_patch(java_box)
    ax.text(10.75, 3.4, "JAVA BILLING & PAYMENT SERVICE (Spring Boot)", 
            fontsize=11, fontweight='bold', color='#f472b6', ha='center')
    ax.text(10.75, 2.55, "• Dynamic Tariff Evaluation Array / Lookup Table: O(1)\n• Safaricom Daraja Lipa na M-Pesa STK Push Service\n• Asynchronous Callback Webhook Receiver\n• FIFO Queue for Pending Callbacks (Strict Arrival Order)\n• Notification Dispatcher (Africa's Talking SMS / Receipts)", 
            fontsize=8.5, color='#cbd5e1', ha='center')

    # Box 5: Database
    db_box = patches.FancyBboxPatch((4.5, 0.2), 5.0, 1.0, boxstyle="round,pad=0.2", 
                                    fc='#0b1120', ec='#94a3b8', lw=1.5, ls='--')
    ax.add_patch(db_box)
    ax.text(7, 0.75, "RELATIONAL PERSISTENCE (PostgreSQL / MySQL / SQLite)", 
            fontsize=10, fontweight='bold', color='#e2e8f0', ha='center')
    ax.text(7, 0.45, "Dynamic Schemas, B-Tree Timestamp Indices & Repository Pattern", 
            fontsize=8.5, color='#94a3b8', ha='center')

    # Arrows
    def draw_arrow(x1, y1, x2, y2, label="", color="#38bdf8", curve=0.0):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2,
                                    shrinkA=5, shrinkB=5,
                                    connectionstyle=f"arc3,rad={curve}"))
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.15, label, fontsize=8, color=color, fontweight='bold', ha='center',
                    bbox=dict(boxstyle="round,pad=0.2", fc='#0f172a', ec=color, lw=0.8))

    # UI <-> Gateway
    draw_arrow(7.0, 7.5, 7.0, 6.6, "REST + WebSocket (/ws/slots)", "#38bdf8")

    # Gateway <-> C++
    draw_arrow(4.8, 4.8, 3.25, 3.8, "HTTP REST (/api/slots/allocate)", "#fbbf24")

    # Gateway <-> Java
    draw_arrow(9.2, 4.8, 10.75, 3.8, "HTTP REST (/api/v1/fee, /stk-push)", "#f472b6")

    # Gateway <-> DB
    draw_arrow(7.0, 4.8, 7.0, 1.2, "SQLAlchemy B-Tree Queries", "#94a3b8")

    # External systems
    ax.text(12.8, 0.9, "Safaricom Daraja API\n(Lipa na M-Pesa Online)", 
            fontsize=8, color='#4ade80', ha='center',
            bbox=dict(boxstyle="round,pad=0.3", fc='#064e3b', ec='#10b981', lw=1))
    draw_arrow(11.5, 1.8, 12.5, 1.2, "STK Push", "#4ade80")

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}")


def create_erd_diagram():
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#0f172a')

    # Title
    ax.text(8, 11.5, "SmartPark KE — Dynamic Relational Database ERD", 
            fontsize=18, fontweight='bold', color='#f8fafc', ha='center', va='center')
    ax.text(8, 11.15, "PostgreSQL / MySQL Schema with B-Tree Indices & Dynamic Tariff Architecture", 
            fontsize=11, color='#94a3b8', ha='center', va='center')

    # Tables definitions: (x, y, w, h, title, fields)
    tables = [
        (1.0, 8.2, 3.2, 2.4, "ZONES", [
            ("zone_id", "SERIAL [PK]"),
            ("zone_name", "VARCHAR(50) [UNIQUE]"),
            ("floor_level", "INT DEFAULT 0"),
            ("created_at", "TIMESTAMP")
        ], '#3b82f6'),
        
        (5.5, 8.2, 4.2, 2.5, "PARKING_SLOTS", [
            ("slot_id", "SERIAL [PK]"),
            ("zone_id", "INT [FK -> zones.zone_id]"),
            ("slot_label", "VARCHAR(10) [UNIQUE]"),
            ("distance_from_entrance", "DECIMAL(6,2)"),
            ("status", "VARCHAR(15) [INDEX]"),
            ("row_position", "INT"),
            ("col_position", "INT"),
            ("vehicle_type", "VARCHAR(20)")
        ], '#10b981'),

        (11.0, 8.2, 3.8, 2.4, "VEHICLES", [
            ("vehicle_id", "SERIAL [PK]"),
            ("plate_number", "VARCHAR(15) [UNIQUE, INDEX]"),
            ("vehicle_type", "VARCHAR(20)"),
            ("created_at", "TIMESTAMP")
        ], '#f59e0b'),

        (5.5, 4.2, 4.5, 3.2, "PARKING_SESSIONS", [
            ("session_id", "SERIAL [PK]"),
            ("vehicle_id", "INT [FK -> vehicles.id]"),
            ("slot_id", "INT [FK -> parking_slots.id]"),
            ("entry_time", "TIMESTAMP [INDEX: B-Tree]"),
            ("exit_time", "TIMESTAMP [INDEX: B-Tree]"),
            ("duration_minutes", "INT"),
            ("fee_charged", "DECIMAL(8,2)"),
            ("paid", "BOOLEAN DEFAULT FALSE"),
            ("status", "VARCHAR(15) [INDEX]")
        ], '#ec4899'),

        (1.0, 4.5, 3.6, 2.5, "TARIFFS (Dynamic Table)", [
            ("tariff_id", "SERIAL [PK]"),
            ("max_minutes", "INT [INDEX]"),
            ("fee", "DECIMAL(8,2)"),
            ("effective_from", "DATE DEFAULT TODAY"),
            ("description", "VARCHAR(100)")
        ], '#8b5cf6'),

        (11.0, 4.2, 4.2, 3.0, "PAYMENTS (M-Pesa STK)", [
            ("payment_id", "SERIAL [PK]"),
            ("session_id", "INT [FK -> sessions.id]"),
            ("phone_number", "VARCHAR(15)"),
            ("amount", "DECIMAL(8,2)"),
            ("mpesa_checkout_request_id", "VARCHAR(60) [UNIQUE]"),
            ("mpesa_receipt_number", "VARCHAR(30) [UNIQUE]"),
            ("result_code", "INT"),
            ("payment_time", "TIMESTAMP")
        ], '#06b6d4'),

        (1.0, 0.8, 4.0, 2.5, "BARRIER_LOGS (FSM Audit)", [
            ("log_id", "SERIAL [PK]"),
            ("session_id", "INT [FK -> sessions.id]"),
            ("barrier_direction", "VARCHAR(10)"),
            ("state", "VARCHAR(15)"),
            ("trigger_source", "VARCHAR(30)"),
            ("changed_at", "TIMESTAMP [INDEX]")
        ], '#eab308'),

        (6.0, 1.0, 3.8, 2.2, "USERS (Auth & RBAC)", [
            ("user_id", "SERIAL [PK]"),
            ("username", "VARCHAR(30) [UNIQUE]"),
            ("password_hash", "VARCHAR(255)"),
            ("role", "VARCHAR(15) [admin/attendant]"),
            ("full_name", "VARCHAR(100)")
        ], '#64748b'),

        (11.0, 1.0, 4.0, 2.2, "NOTIFICATIONS (FIFO SMS)", [
            ("notification_id", "SERIAL [PK]"),
            ("session_id", "INT [FK -> sessions.id]"),
            ("channel", "VARCHAR(10)"),
            ("recipient", "VARCHAR(100)"),
            ("content", "TEXT"),
            ("status", "VARCHAR(15) [INDEX]")
        ], '#14b8a6')
    ]

    for x, y, w, h, title, fields, border_color in tables:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", 
                                     fc='#1e293b', ec=border_color, lw=2)
        ax.add_patch(box)
        
        # Header banner
        header = patches.Rectangle((x - 0.15, y + h - 0.5), w + 0.3, 0.55, 
                                   fc=border_color, ec='none')
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 0.25, title, fontsize=9.5, fontweight='bold', 
                color='#ffffff', ha='center', va='center')
        
        # Fields
        cur_y = y + h - 0.8
        for field, ftype in fields:
            ax.text(x + 0.1, cur_y, field, fontsize=7.5, fontweight='600', color='#f1f5f9', va='center')
            ax.text(x + w - 0.1, cur_y, ftype, fontsize=7, color='#94a3b8', ha='right', va='center')
            cur_y -= 0.25

    # Connectors
    def draw_relation(x1, y1, x2, y2, label="1 : N"):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color='#60a5fa', lw=1.5,
                                    shrinkA=5, shrinkB=5))
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my, label, fontsize=7.5, color='#93c5fd', 
                bbox=dict(boxstyle="round,pad=0.1", fc='#0f172a', ec='#60a5fa', lw=0.5))

    # Zones -> Slots
    draw_relation(4.2, 9.4, 5.5, 9.4, "1 : N")
    # Slots -> Sessions
    draw_relation(7.6, 8.2, 7.6, 7.4, "1 : N")
    # Vehicles -> Sessions
    draw_relation(11.0, 9.0, 10.0, 7.0, "1 : N")
    # Sessions -> Payments
    draw_relation(10.0, 5.7, 11.0, 5.7, "1 : N")
    # Sessions -> Barrier Logs
    draw_relation(5.5, 5.0, 3.5, 3.3, "1 : N")
    # Sessions -> Notifications
    draw_relation(9.5, 4.2, 11.0, 2.5, "1 : N")

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "ERD_diagram.png")
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    create_architecture_diagram()
    create_erd_diagram()
