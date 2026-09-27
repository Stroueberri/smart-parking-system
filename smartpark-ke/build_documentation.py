"""
SmartPark KE — Comprehensive System Documentation Generator
Generates:
 1. docs/algorithms_pseudocode.pdf
 2. docs/SmartPark_KE_System_Documentation.docx
 3. docs/SmartPark_KE_System_Documentation.pdf
"""

import os
import sys
from datetime import datetime

# Docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

ARCH_IMG = os.path.join(DOCS_DIR, "architecture_diagram.png")
ERD_IMG = os.path.join(DOCS_DIR, "ERD_diagram.png")


# ============================================================================
# 1. GENERATE DOCX DOCUMENT
# ============================================================================
def generate_docx():
    docx_path = os.path.join(DOCS_DIR, "SmartPark_KE_System_Documentation.docx")
    doc = Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Helper styling functions
    def set_cell_background(cell, fill_hex):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    # Document Header / Cover
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("SMARTPARK KE\n")
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(37, 99, 235)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Intelligent Automated Parking Management System\nTechnical Architecture, Data Structures & Algorithmic Blueprint")
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # Metadata Box
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Client Jurisdiction:", "Republic of Kenya (Safaricom Daraja Lipa na M-Pesa Online)"),
        ("System Architecture:", "Polyglot Microservices: Python (Gateway), C++ (Slot Engine), Java (Billing)"),
        ("Author / Team:", "Google DeepMind Advanced Agentic Coding Pair (Antigravity)"),
        ("Date / Version:", "September 2026 / Version 2.0 (Production Blueprint)"),
        ("Status:", "Fully Tested, Dockerized & Functional Repository Deliverable")
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.text = k
        c0.paragraphs[0].runs[0].font.bold = True
        c1.text = v
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")

    doc.add_page_break()

    # SECTION 1: PROBLEM ANALYSIS & TERMS OF REFERENCE
    doc.add_heading("1. Problem Analysis & Terms of Reference", level=1)
    doc.add_paragraph(
        "Commercial and municipal parking operations across urban Kenyan centers (Nairobi CBD, Westlands, Upper Hill, Mombasa) "
        "suffer from severe operational bottlenecks: manual ticket dispensing, slow physical cash/card reconciliation, "
        "congestion at entry gates due to lack of real-time bay guidance, and revenue leakage. "
        "The SmartPark KE system was commissioned to automate end-to-end parking management under the following strict terms of reference:"
    )

    reqs = [
        ("Visual Display Before Entry:", "Drivers must view an authoritative live color-coded visual map of available parking bays prior to entry."),
        ("Arrival Registration:", "Every arriving vehicle must be recorded on entry (plate number, timestamp, vehicle type)."),
        ("Exit Calculation:", "On exit, the system must automatically calculate total elapsed parking duration and amount due."),
        ("Automated Barrier Release:", "The barrier gate actuator must automatically raise once parking fees are verified."),
        ("Mobile Money Integration:", "Payment must be collected via Safaricom Lipa na M-Pesa STK Push directly at checkout."),
        ("Nearest Slot Allocation:", "Incoming vehicles must be automatically routed to the closest free slot relative to the entrance."),
        ("Real-Time Duration Tracking:", "The system must track parking duration per vehicle continuously in memory, not just at exit."),
        ("Fixed Tariff Schedule:", "Up to 30 min (Free), Up to 2 hours (50 Kshs), Up to 4 hours (100 Kshs), Up to 6 hours (300 Kshs), Over 6 hours (500 Kshs)."),
        ("Polyglot Microservice Architecture:", "Python, C++, and Java must each perform distinct, non-decorative engineering roles.")
    ]
    for r_title, r_desc in reqs:
        p = doc.add_paragraph(style='List Bullet')
        r_t = p.add_run(r_title + " ")
        r_t.font.bold = True
        p.add_run(r_desc)

    # SECTION 2: POLYGLOT SYSTEM ARCHITECTURE
    doc.add_heading("2. Polyglot Microservices Architecture", level=1)
    doc.add_paragraph(
        "To achieve maximum throughput, rock-solid transactional safety, and rapid UI interactivity, SmartPark KE employs "
        "a polyglot microservice design where each language is strictly assigned to its optimal engineering domain:"
    )

    doc.add_paragraph(
        "• C++17 Slot Engine & Barrier Actuator (Port 8081): Performance-critical in-memory engine managing the slot Min-Heap, "
        "weighted graph Dijkstra pathfinding, physical row doubly linked lists, and the actuator Finite State Machine (FSM) with a LIFO audit stack.\n"
        "• Java 17 / Spring Boot Billing Service (Port 8082): Transactional billing engine computing tariffs via dynamic arrays, "
        "executing Safaricom Daraja Lipa na M-Pesa STK Push requests, processing asynchronous webhooks via a FIFO Queue, and dispatching SMS receipts.\n"
        "• Python 3.11+ / Flask-SocketIO Gateway (Port 5000): Serves responsive HTML5/JS web clients, manages central relational persistence "
        "(SQLAlchemy repository pattern), performs active duration tracking with an in-memory Min-Heap, and broadcasts live slot diffs over WebSockets."
    )

    if os.path.exists(ARCH_IMG):
        doc.add_paragraph().paragraph_format.space_after = Pt(10)
        doc.add_picture(ARCH_IMG, width=Inches(6.2))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_run = cap.add_run("Figure 1: SmartPark KE Polyglot Microservices Inter-Service Architecture")
        cap_run.font.italic = True
        cap_run.font.size = Pt(9)

    doc.add_page_break()

    # SECTION 3: ALL 11 MODULES & ALGORITHMS (PSEUDOCODE)
    doc.add_heading("3. Functional Modules & Algorithmic Specifications", level=1)
    doc.add_paragraph("The system implements 11 fully functional modules (exceeding the required minimum of 8):")

    modules = [
        ("Module 1 — Vehicle Entry & Registration (Python + C++)",
         "Hash Map <plate_number, VehicleSession> for O(1) duplicate checks and lookup.",
         """ALGORITHM VehicleEntry(plate, vehicle_type):
    plate = SanitizeAndUppercase(plate)
    if plate in ActiveSessionsHashMap:
        return Error("Vehicle already parked inside", 409)
    slot = SlotEngineClient.AllocateNearestSlot()
    if slot is NULL:
        return Error("Parking lot completely full", 400)
    session = CreateSession(plate, slot.id, CurrentTime())
    ActiveSessionsHashMap.Insert(plate, session)
    TimeTrackerHeap.Push(session.entry_time, session)
    WebSocket.BroadcastSlotState(slot.id, "OCCUPIED", plate)
    return session"""),

        ("Module 2 — Nearest Slot Allocation Engine (C++)",
         "Binary Min-Heap (priority queue) of free slots keyed by distance O(log n); Adjacency-list Graph + Dijkstra O((V+E)log V); Doubly Linked List per row O(1).",
         """ALGORITHM AllocateNearestSlot():
    if FreeSlotsMinHeap.IsEmpty():
        return NULL
    nearest_slot = FreeSlotsMinHeap.ExtractMin() // O(log n)
    row_list = ZoneRowLists[nearest_slot.zoneId]
    row_list.UpdateStatus(nearest_slot.slotId, "OCCUPIED") // O(1)
    return nearest_slot

ALGORITHM ReleaseSlot(slot_id):
    slot = AllSlotsMap[slot_id]
    FreeSlotsMinHeap.Insert(slot) // O(log n)
    row_list = ZoneRowLists[slot.zoneId]
    row_list.UpdateStatus(slot_id, "FREE") // O(1)"""),

        ("Module 3 — Real-Time Visual Slot Display (Python + JS)",
         "In-memory 2D Array/Matrix mirroring physical grid (rows x bays); WebSocket diff broadcaster.",
         """ALGORITHM BroadcastSlotDiff(slot_id, new_status, plate):
    slot_matrix[row][col].status = new_status
    payload = {slotId: slot_id, status: new_status, currentPlate: plate}
    WebSocket.Emit("slot_state_changed", payload) // Pushes O(1) delta to browser DOM"""),

        ("Module 4 — Time Tracking & Overstay Detection (Python + C++)",
         "Hash Map (plate -> entry_time) combined with Min-Heap ordered by entry_time.",
         """ALGORITHM OverstayAlertScan(threshold_minutes):
    alerts = []
    now = CurrentTime()
    while TimeTrackerHeap.NotEmpty() and ElapsedMinutes(TimeTrackerHeap.Peek().entry_time, now) >= threshold_minutes:
        vehicle = TimeTrackerHeap.Pop()
        if vehicle.isActive:
            alerts.Append(vehicle)
    return alerts // O(k log n) without scanning entire database"""),

        ("Module 5 — Fee Calculation Module (Java)",
         "Lookup Array/Table of (upper_bound_minutes, fee) tuples scanned linearly in O(1).",
         """ALGORITHM CalculateParkingFee(duration_minutes):
    duration = Max(0, duration_minutes)
    for tier in TariffLookupTable:
        if duration <= tier.maxMinutes:
            return tier.fee
    return 500.00 // Default over-6-hour rate"""),

        ("Module 6 — Payment Module: M-Pesa STK Push (Java / Spring Boot)",
         "FIFO Queue of pending payment callbacks; Hash Map of CheckoutRequestID -> Request.",
         """ALGORITHM InitiateMpesaStkPush(sessionId, phone, amount):
    phone_normalized = FormatKenyanNumber(phone) // 2547XXXXXXXX
    timestamp = CurrentTimestamp("yyyyMMddHHmmss")
    password = Base64(ShortCode + PassKey + timestamp)
    checkout_id = GenerateCheckoutID()
    PendingCheckoutsMap.Put(checkout_id, {sessionId, phone, amount})
    DarajaAPI.SendSTKRequest(ShortCode, password, timestamp, amount, phone, CallbackURL)
    return checkout_id

ALGORITHM OnDarajaWebhookReceived(payload):
    CallbackQueue.Offer(payload) // FIFO Queue
    while not CallbackQueue.IsEmpty():
        event = CallbackQueue.Poll()
        if event.ResultCode == 0:
            MarkSessionPaid(event.checkoutRequestId)
            TriggerBarrierOpen(event.sessionId)
            NotificationDispatcher.EnqueueReceipt(event)"""),

        ("Module 7 — Barrier Control Module (C++ Simulated Actuator)",
         "Actuator Finite State Machine (CLOSED -> OPENING -> OPEN -> CLOSING -> CLOSED); LIFO Stack audit log.",
         """ALGORITHM HandleBarrierPaymentConfirmed(sessionId):
    if currentState in [CLOSED, CLOSING]:
        currentState = OPENING
        log = {from: "CLOSED", to: "OPENING", trigger: "PAYMENT_CONFIRMED", sessionId}
        AuditStack.Push(log) // O(1) LIFO Stack
        MechanicalActuator.Open()
        currentState = OPEN
        return True
    return False"""),

        ("Module 8 — Database Management Module (Python / SQLAlchemy)",
         "Repository pattern isolating SQL writes; B-Tree indices on foreign keys and timestamps.",
         """ALGORITHM RepositoryWriteSession(session_data):
    db_session = SessionLocal()
    try:
        db_session.Add(session_data)
        db_session.Commit()
    catch Exception as e:
        db_session.Rollback()
        raise e
    finally:
        db_session.Close()"""),

        ("Module 9 — Admin & Reporting Module (Python)",
         "B-Tree range queries across entry_time/exit_time; Min-Heap overstay inspection.",
         """ALGORITHM GenerateRevenueReport(startDate, endDate):
    return DB.Query(ParkingSessions)
             .Filter(entry_time >= startDate, exit_time <= endDate, paid == True)
             .Aggregate(Sum(fee_charged), Count(session_id))"""),

        ("Module 10 — Authentication & Role-Based Access Control (Python)",
         "In-memory session token Hash Map; bcrypt password hashing; role decorators.",
         """ALGORITHM AuthenticateUser(username, raw_password):
    user = DB.FindUser(username)
    if user and VerifyBcryptHash(user.password_hash, raw_password):
        token = GenerateSecureToken()
        ActiveSessionHashMap.Put(token, user.role)
        return token
    return Unauthorized()"""),

        ("Module 11 — Notification Module (Java / Spring Boot + Python)",
         "FIFO Queue for outbound SMS/Email receipts; Africa's Talking API compatible format.",
         """ALGORITHM EnqueueAndDispatchSmsReceipt(sessionId, phone, plate, amount, receipt):
    job = {phone, plate, amount, receipt, messageText}
    NotificationQueue.Offer(job) // FIFO Queue
    worker = NotificationQueue.Poll()
    AfricasTalkingGateway.SendSMS(worker.phone, worker.messageText)""")
    ]

    for title, ds, algo in modules:
        doc.add_heading(title, level=2)
        p_ds = doc.add_paragraph()
        p_ds.add_run("Underlying Data Structure: ").font.bold = True
        p_ds.add_run(ds)
        p_code = doc.add_paragraph(algo)
        p_code.paragraph_format.left_indent = Inches(0.25)
        for r in p_code.runs:
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_page_break()

    # SECTION 4: DATA STRUCTURES SUMMARY TABLE
    doc.add_heading("4. Comprehensive Data Structures Summary Table", level=1)
    doc.add_paragraph("Table 1 summarizes every data structure utilized across the 11 modules, with Big-O time/space complexities and engineering justifications:")

    ds_table = doc.add_table(rows=1, cols=5)
    ds_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = ds_table.rows[0].cells
    hdr_titles = ["Data Structure", "Used In", "Operations", "Complexity", "Engineering Justification"]
    for i, t in enumerate(hdr_titles):
        hdr[i].text = t
        hdr[i].paragraphs[0].runs[0].font.bold = True
        set_cell_background(hdr[i], "1E293B")
        hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    ds_rows = [
        ("Hash Map", "Modules 1, 4, 10", "Get, Insert, Delete", "O(1) avg", "O(1) instant duplicate check on arrival, token validation, and plate stay lookups."),
        ("Min-Heap (Priority Queue)", "Module 2 (Slots), Module 4 (Time)", "Push, Pop, Peek", "O(log n) push/pop, O(1) peek", "Extracts nearest bay by distance in O(log n); peeks oldest vehicle for overstay alerts without scanning all records."),
        ("Weighted Graph + Dijkstra", "Module 2 (Multi-Floor)", "Shortest Path Search", "O((V+E)log V)", "Accurately models physical driveway lanes, ramps, and turning angles across multi-level decks."),
        ("Doubly Linked List", "Module 2 (Physical Rows)", "InsertAfter, UpdateStatus", "O(1) insert/update", "Re-inserts freed bays next to physical neighbors in O(1), keeping physical bay display synchronized."),
        ("2D Array / Matrix", "Module 3 (Visual Display)", "Cell Lookup / Update", "O(1) access", "Mirrors physical parking bays (rows × bays) for zero-overhead browser rendering."),
        ("FIFO Queue", "Modules 6, 11", "Enqueue, Dequeue", "O(1)", "Guarantees in-order processing of asynchronous Daraja payment callbacks and retry-safe SMS dispatches."),
        ("LIFO Stack", "Module 7 (Barrier FSM)", "Push, Peek", "O(1)", "Chronological audit trail of gate actuator states; peek provides instant O(1) inspection of what just happened."),
        ("Lookup Array / Table", "Module 5 (Tariff Engine)", "Linear Tier Scan", "O(1) constant", "Fixed small tariff table (5 tiers) scanned linearly; eliminates unnecessary tree or hash overhead."),
        ("B-Tree (Relational Index)", "Module 8, 9 (Database)", "Range Queries on Dates", "O(log N)", "Native PostgreSQL/MySQL B-Tree index enables ultra-fast range queries on entry_time and exit_time.")
    ]

    for item in ds_rows:
        row = ds_table.add_row().cells
        for col_idx, text in enumerate(item):
            row[col_idx].text = text
            row[col_idx].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_background(row[col_idx], "F8FAFC" if col_idx % 2 == 0 else "FFFFFF")

    doc.add_page_break()

    # SECTION 5: RELATIONAL DATABASE & ERD
    doc.add_heading("5. Relational Database Design & Schema Architecture", level=1)
    doc.add_paragraph(
        "SmartPark KE implements a dynamic, fully data-driven relational schema compatible with PostgreSQL, MySQL 8.0, and SQLite. "
        "Tariff rates, slot dimensions, and multi-level zones are stored directly in configurable tables rather than hardcoded in application logic."
    )

    if os.path.exists(ERD_IMG):
        doc.add_picture(ERD_IMG, width=Inches(6.2))
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_run2 = cap2.add_run("Figure 2: Dynamic Entity-Relationship Diagram (ERD) with B-Tree Indices")
        cap_run2.font.italic = True
        cap_run2.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # SECTION 6: PAYMENT SEQUENCE DIAGRAM
    doc.add_heading("6. Safaricom Daraja Lipa na M-Pesa STK Push Sequence", level=1)
    doc.add_paragraph(
        "The STK push workflow connects the Driver, Web Gateway, Java Billing Microservice, Safaricom Daraja API, and C++ Barrier Actuator:"
    )

    seq_steps = [
        "1. Driver arrives at checkout kiosk; Attendant enters vehicle plate number.",
        "2. Python Gateway computes duration and queries Java Billing Service (Module 5) for fee.",
        "3. Attendant confirms mobile number; Web Gateway dispatches STK Push request to Java Service.",
        "4. Java Service formats phone number, generates Daraja password, and calls Safaricom STK Push API.",
        "5. Safaricom Daraja pushes secure USSD prompt to driver's phone; driver enters 4-digit M-Pesa PIN.",
        "6. Safaricom Daraja dispatches asynchronous HTTP POST callback to Java Service /api/v1/payment/callback.",
        "7. Java Service enqueues callback into FIFO Queue, matches CheckoutRequestID in O(1), and verifies ResultCode == 0.",
        "8. Java Service notifies Python Gateway, marks session paid in PostgreSQL, and dispatches SMS receipt via Queue.",
        "9. Python Gateway signals C++ Barrier Engine; actuator transitions CLOSED -> OPENING -> OPEN.",
        "10. Driver departs; vehicle sensor detects passage and signals gate to CLOSE (logged in LIFO Stack)."
    ]
    for step in seq_steps:
        doc.add_paragraph(step, style='List Number')

    doc.add_page_break()

    # SECTION 7: SETUP & RUN INSTRUCTIONS
    doc.add_heading("7. Setup, Installation & Verification Instructions", level=1)
    doc.add_paragraph("The entire system can be run in two modes: automated Docker Compose orchestration or standalone native execution.")

    doc.add_heading("Option A: Docker Compose (All Services in 1 Command)", level=2)
    p_dock = doc.add_paragraph(
        "$ git clone https://github.com/smartpark-ke/smartpark-ke.git\n"
        "$ cd smartpark-ke\n"
        "$ cp .env.example .env\n"
        "$ docker-compose up --build"
    )
    for r in p_dock.runs:
        r.font.name = "Consolas"
        r.font.size = Pt(9)

    doc.add_heading("Option B: Standalone Execution (Development Mode)", level=2)
    p_dev = doc.add_paragraph(
        "# Terminal 1: Run C++ Slot Allocation Engine\n"
        "$ cd slot-engine-cpp\n"
        "$ mkdir build && cd build && cmake .. && make\n"
        "$ ./slot_engine 8081\n\n"
        "# Terminal 2: Run Java Billing & Payment Service\n"
        "$ cd billing-payment-java\n"
        "$ mvn spring-boot:run\n\n"
        "# Terminal 3: Run Python Web Gateway\n"
        "$ cd web-gateway-python\n"
        "$ pip install -r requirements.txt\n"
        "$ python app.py"
    )
    for r in p_dev.runs:
        r.font.name = "Consolas"
        r.font.size = Pt(9)

    doc.add_heading("Service Access URLs", level=2)
    doc.add_paragraph(
        "• Public Driver Display: http://localhost:5000/\n"
        "• Attendant Checkout & M-Pesa Kiosk: http://localhost:5000/attendant\n"
        "• Admin Analytics Dashboard: http://localhost:5000/admin\n"
        "• C++ Slot Engine Health: http://localhost:8081/health\n"
        "• Java Billing API Health: http://localhost:8082/api/v1/health"
    )

    doc.save(docx_path)
    print(f"Generated DOCX: {docx_path}")


# ============================================================================
# 2. GENERATE PDF DOCUMENTS (ReportLab)
# ============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SmartPark KE — Intelligent Automated Parking System | System Documentation")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — KENYA PARKING AUTOMATION SPECIFICATION")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def generate_system_documentation_pdf():
    pdf_path = os.path.join(DOCS_DIR, "SmartPark_KE_System_Documentation.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=colors.HexColor("#1e3a8a"), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=16, textColor=colors.HexColor("#64748b"), alignment=1)
    h1_style = ParagraphStyle('H1Style', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor("#0f172a"), spaceBefore=14, spaceAfter=8)
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor("#2563eb"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#334155"), spaceAfter=6)
    bullet_style = ParagraphStyle('BulletStyle', parent=body_style, leftIndent=12, firstLineIndent=-8, spaceAfter=3)
    code_style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=10, textColor=colors.HexColor("#0f172a"), backColor=colors.HexColor("#f8fafc"), leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=8)

    story = []

    # Title & Metadata
    story.append(Spacer(1, 20))
    story.append(Paragraph("SMARTPARK KE", title_style))
    story.append(Paragraph("Intelligent Automated Parking Management System<br/>Technical Blueprint, Polyglot Architecture &amp; Data Structures Report", subtitle_style))
    story.append(Spacer(1, 20))

    meta_table_data = [
        [Paragraph("<b>Target Jurisdiction:</b>", body_style), Paragraph("Republic of Kenya (Safaricom Lipa na M-Pesa Integration)", body_style)],
        [Paragraph("<b>Polyglot Services:</b>", body_style), Paragraph("Python (Web Gateway) &bull; C++17 (Slot Engine) &bull; Java 17 (Billing)", body_style)],
        [Paragraph("<b>Persistence:</b>", body_style), Paragraph("Dynamic PostgreSQL / MySQL Schema with B-Tree Indices", body_style)],
        [Paragraph("<b>Tariff Model:</b>", body_style), Paragraph("Dynamic Data-Driven Table (0 to 30m Free, 50, 100, 300, 500 Kshs)", body_style)],
        [Paragraph("<b>Author / System:</b>", body_style), Paragraph("Google DeepMind Advanced Agentic Coding Pair (Antigravity)", body_style)]
    ]
    t = Table(meta_table_data, colWidths=[140, 360])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # 1. Problem Analysis
    story.append(Paragraph("1. Problem Analysis &amp; Client Terms of Reference", h1_style))
    story.append(Paragraph(
        "Commercial and municipal parking operations across urban centers in Kenya encounter major operational bottlenecks: "
        "manual gate ticketing, slow cash and card reconciliation, congestion at entrance gates due to absent real-time bay guidance, "
        "and revenue leakage. SmartPark KE was engineered to provide a fully automated, modern web-based parking management system "
        "conforming strictly to the client terms of reference below:", body_style
    ))
    story.append(Paragraph("&bull; <b>Pre-Entry Visual Display:</b> Real-time visual color-coded layout of bays before entry.", bullet_style))
    story.append(Paragraph("&bull; <b>Vehicle Registration:</b> Automatic timestamped check-in recording plate number and vehicle category.", bullet_style))
    story.append(Paragraph("&bull; <b>Automated Exit Calculation:</b> Automatic elapsed duration computation and tariff calculation on exit.", bullet_style))
    story.append(Paragraph("&bull; <b>Automated Barrier Actuator:</b> Barrier automatically lifts upon verified fee payment.", bullet_style))
    story.append(Paragraph("&bull; <b>Mobile Money Integration:</b> Safaricom Daraja Lipa na M-Pesa STK Push direct to customer phone.", bullet_style))
    story.append(Paragraph("&bull; <b>Nearest Slot Allocation:</b> Min-Heap and Dijkstra graph routing allocating closest available bay.", bullet_style))
    story.append(Paragraph("&bull; <b>Real-Time Stay Tracking:</b> Continuous in-memory duration tracking and overstay detection.", bullet_style))
    story.append(Paragraph("&bull; <b>Fixed Tariff Schedule:</b> 0-30 min (Free), 2h (50 Kshs), 4h (100 Kshs), 6h (300 Kshs), >6h (500 Kshs).", bullet_style))

    # 2. Architecture
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Polyglot Microservices Architecture", h1_style))
    story.append(Paragraph(
        "The architecture decomposes system responsibilities across three languages suited to their specialized operational profiles:", body_style
    ))
    story.append(Paragraph("&bull; <b>C++17 Engine (Port 8081):</b> Manages the free-slot Min-Heap, multi-floor driving Graph Dijkstra shortest-paths, physical row Doubly Linked Lists, and the barrier Finite State Machine (FSM) with a LIFO audit stack.", bullet_style))
    story.append(Paragraph("&bull; <b>Java 17 Spring Boot (Port 8082):</b> Manages dynamic tariff array scans, Safaricom Daraja STK Push requests, asynchronous callback webhook processing via a FIFO Queue, and SMS receipt dispatch.", bullet_style))
    story.append(Paragraph("&bull; <b>Python 3.11 Gateway (Port 5000):</b> Serves HTML5/JS clients, handles active session hash maps, overstay min-heap peek checks, relational persistence via SQLAlchemy, and pushes live slot diffs over WebSockets.", bullet_style))

    if os.path.exists(ARCH_IMG):
        story.append(Spacer(1, 10))
        story.append(Image(ARCH_IMG, width=500, height=350))
        story.append(Paragraph("<i>Figure 1: Polyglot Microservices Architecture and Inter-Service REST/WebSocket Communication</i>", ParagraphStyle('Cap', parent=body_style, fontSize=8, alignment=1, textColor=colors.HexColor("#64748b"))))

    story.append(PageBreak())

    # 3. Data Structures
    story.append(Paragraph("3. Data Structures Summary &amp; Algorithmic Justifications", h1_style))
    story.append(Paragraph(
        "Every data structure in SmartPark KE was selected based on Big-O algorithmic guarantees to ensure maximum responsiveness and zero bottlenecks:", body_style
    ))

    ds_table_data = [
        [Paragraph("<b>Data Structure</b>", body_style), Paragraph("<b>Module</b>", body_style), Paragraph("<b>Time Complexity</b>", body_style), Paragraph("<b>Engineering Justification</b>", body_style)],
        [Paragraph("Hash Map", body_style), Paragraph("1, 4, 10", body_style), Paragraph("O(1) Get/Put", body_style), Paragraph("Instant duplicate check on entry, active stay lookup, and auth token validation.", body_style)],
        [Paragraph("Min-Heap", body_style), Paragraph("2, 4", body_style), Paragraph("O(log n) Push/Pop<br/>O(1) Peek", body_style), Paragraph("Allocates closest bay by distance in O(log n); peeks oldest vehicle for overstay alerts in O(1).", body_style)],
        [Paragraph("Weighted Graph + Dijkstra", body_style), Paragraph("2", body_style), Paragraph("O((V+E)log V)", body_style), Paragraph("Computes exact multi-floor driving distances across ramps, aisles, and turning radiuses.", body_style)],
        [Paragraph("Doubly Linked List", body_style), Paragraph("2", body_style), Paragraph("O(1) Insert/Update", body_style), Paragraph("Re-inserts freed bay next to physical neighbors in O(1), keeping visual ordering pristine.", body_style)],
        [Paragraph("2D Matrix Array", body_style), Paragraph("3", body_style), Paragraph("O(1) Cell Access", body_style), Paragraph("Directly mirrors physical bays (rows × cols) for real-time browser rendering.", body_style)],
        [Paragraph("FIFO Queue", body_style), Paragraph("6, 11", body_style), Paragraph("O(1) Enqueue/Deq", body_style), Paragraph("Preserves strict arrival order of asynchronous Daraja payment callbacks and SMS jobs.", body_style)],
        [Paragraph("LIFO Stack", body_style), Paragraph("7", body_style), Paragraph("O(1) Push/Peek", body_style), Paragraph("Maintains chronological audit trail of gate transitions; top yields most recent event.", body_style)],
        [Paragraph("Lookup Table", body_style), Paragraph("5", body_style), Paragraph("O(1) Tier Scan", body_style), Paragraph("Scans small dynamic tariff list (5 tiers) linearly with zero overhead.", body_style)],
        [Paragraph("B-Tree (DB Index)", body_style), Paragraph("8, 9", body_style), Paragraph("O(log N) Range", body_style), Paragraph("Relational database index enabling ultra-fast range queries on entry and exit timestamps.", body_style)]
    ]

    t_ds = Table(ds_table_data, colWidths=[100, 50, 90, 260])
    t_ds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_ds)

    story.append(Spacer(1, 15))

    # 4. Database Schema
    story.append(Paragraph("4. Dynamic Relational Database Design", h1_style))
    story.append(Paragraph(
        "The relational database schema is fully dynamic and data-driven. Tariff schedules, multi-level zones, "
        "and bay geometries are stored in configurable tables rather than hardcoded:", body_style
    ))

    if os.path.exists(ERD_IMG):
        story.append(Image(ERD_IMG, width=500, height=360))
        story.append(Paragraph("<i>Figure 2: Dynamic Relational Database ERD with B-Tree Indices and Foreign Key Topology</i>", ParagraphStyle('Cap2', parent=body_style, fontSize=8, alignment=1, textColor=colors.HexColor("#64748b"))))

    story.append(PageBreak())

    # 5. Core Algorithmic Pseudocode (All 11 Modules)
    story.append(Paragraph("5. Algorithmic Pseudocode Specifications (All 11 Modules)", h1_style))

    algos = [
        ("Module 1: Vehicle Entry & Registration",
         "// O(1) duplicate check + session creation\n"
         "function RegisterArrival(plateNumber, vehicleType):\n"
         "    if ActiveSessionsHashMap.contains(plateNumber):\n"
         "        throw DuplicateEntryException(\"Vehicle already inside lot\")\n"
         "    slot = SlotEngineClient.allocateNearestSlot()\n"
         "    session = DB.createSession(plateNumber, slot.id, CurrentTime())\n"
         "    ActiveSessionsHashMap.put(plateNumber, session)\n"
         "    TimeTrackerMinHeap.push(session.entryTime, session)\n"
         "    WebSocket.broadcastSlotDiff(slot.id, \"OCCUPIED\", plateNumber)\n"
         "    return session"),

        ("Module 2: Nearest Slot Allocation (C++ Min-Heap + Dijkstra)",
         "// O(log n) slot extraction from MinHeap\n"
         "function ExtractNearestSlot():\n"
         "    if freeSlotsHeap.isEmpty():\n"
         "        return NULL\n"
         "    nearest = freeSlotsHeap.extractMin() // O(log n)\n"
         "    rowList = zoneRowDoublyLinkedLists[nearest.zoneId]\n"
         "    rowList.updateStatus(nearest.slotId, \"OCCUPIED\") // O(1)\n"
         "    return nearest\n\n"
         "// Dijkstra shortest driving path calculation across multi-floor lot\n"
         "function DijkstraShortestPaths(entranceNodeId):\n"
         "    dist[v] = INFINITY for all v; dist[entranceNodeId] = 0\n"
         "    pq.push((0, entranceNodeId))\n"
         "    while not pq.isEmpty():\n"
         "        (currDist, u) = pq.pop()\n"
         "        for edge in adjList[u]:\n"
         "            if dist[u] + edge.weight < dist[edge.v]:\n"
         "                dist[edge.v] = dist[u] + edge.weight\n"
         "                pred[edge.v] = u\n"
         "                pq.push((dist[edge.v], edge.v))\n"
         "    return dist, pred"),

        ("Module 5: Fee Calculation (Java Dynamic Tariff Table)",
         "// O(1) linear scan through dynamic tariff array\n"
         "function CalculateFee(durationMinutes):\n"
         "    duration = max(0, durationMinutes)\n"
         "    for tier in dynamicTariffTable:\n"
         "        if duration <= tier.maxMinutes:\n"
         "            return tier.fee\n"
         "    return 500.00 // Default over-6-hour rate"),

        ("Module 6: Safaricom Daraja Lipa na M-Pesa STK Push",
         "// Initiates STK Push & enqueues asynchronous callback in FIFO order\n"
         "function ProcessStkPush(sessionId, phone, amount):\n"
         "    normPhone = FormatKenyanNumber(phone) // 2547XXXXXXXX\n"
         "    timestamp = CurrentDateTime(\"yyyyMMddHHmmss\")\n"
         "    password = Base64(ShortCode + PassKey + timestamp)\n"
         "    checkoutId = DarajaAPI.sendSTKPrompt(normPhone, amount, password, timestamp)\n"
         "    PendingPaymentsMap.put(checkoutId, {sessionId, amount, normPhone})\n"
         "    return checkoutId\n\n"
         "function OnDarajaWebhook(callbackPayload):\n"
         "    FifoCallbackQueue.offer(callbackPayload) // FIFO Queue\n"
         "    while not FifoCallbackQueue.isEmpty():\n"
         "        event = FifoCallbackQueue.poll()\n"
         "        if event.resultCode == 0:\n"
         "            ConfirmPaymentAndOpenBarrier(event.checkoutRequestId)"),

        ("Module 7: Barrier Actuator State Machine (LIFO Audit Stack)",
         "// FSM: CLOSED -> OPENING -> OPEN -> CLOSING -> CLOSED\n"
         "function TriggerBarrierOpen(sessionId):\n"
         "    if currentState == CLOSED or currentState == CLOSING:\n"
         "        currentState = OPENING\n"
         "        log = {from: \"CLOSED\", to: \"OPENING\", trigger: \"PAYMENT_CONFIRMED\", sessionId}\n"
         "        AuditStack.push(log) // O(1) LIFO Stack\n"
         "        ActuatorHardware.raiseBoomArm()\n"
         "        currentState = OPEN\n"
         "        return true\n"
         "    return false")
    ]

    for title, code in algos:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {pdf_path}")


def generate_algorithms_pseudocode_pdf():
    pdf_path = os.path.join(DOCS_DIR, "algorithms_pseudocode.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor("#1e3a8a"), alignment=1)
    h1_style = ParagraphStyle('H1Style', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor("#0f172a"), spaceBefore=12, spaceAfter=6)
    code_style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=11, textColor=colors.HexColor("#0f172a"), backColor=colors.HexColor("#f8fafc"), leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=8)

    story = []
    story.append(Paragraph("SMARTPARK KE — ALGORITHMIC SPECIFICATION", title_style))
    story.append(Paragraph("Complete Pseudocode Breakdown for All 11 Polyglot Modules", ParagraphStyle('Sub', parent=styles['Normal'], alignment=1, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 15))

    algos = [
        ("Module 1 — Vehicle Entry & Registration (Python + C++)",
         "Data Structure: Hash Map <plate_number, VehicleSession> [O(1) lookup]\n\n"
         "Algorithm EntryRegistration(plate, type):\n"
         "    clean_plate = SanitizeAndUppercase(plate)\n"
         "    if ActiveSessionMap.contains(clean_plate):\n"
         "        throw DuplicateException(\"Vehicle already inside\")\n"
         "    slot = SlotEngineClient.requestNearestSlot()\n"
         "    session = DB.insertParkingSession(clean_plate, slot.id, now())\n"
         "    ActiveSessionMap.put(clean_plate, session)\n"
         "    TimeTrackerHeap.insert(session.entry_time, session)\n"
         "    WebSocket.emit(\"slot_state_changed\", {slot.id, \"OCCUPIED\", clean_plate})\n"
         "    return session"),

        ("Module 2 — Nearest Slot Allocation Engine (C++)",
         "Data Structures: Min-Heap [O(log n)], Graph Dijkstra [O((V+E)log V)], Doubly Linked List [O(1)]\n\n"
         "Algorithm ExtractMinSlot():\n"
         "    if freeMinHeap.empty(): return NULL\n"
         "    nearest = freeMinHeap.extractMin() // O(log n)\n"
         "    rowList = zoneLists[nearest.zoneId]\n"
         "    rowList.updateStatus(nearest.slotId, \"OCCUPIED\") // O(1)\n"
         "    return nearest\n\n"
         "Algorithm ReleaseSlot(slotId):\n"
         "    slot = allSlots[slotId]\n"
         "    freeMinHeap.insert(slot) // O(log n)\n"
         "    zoneLists[slot.zoneId].updateStatus(slotId, \"FREE\") // O(1)"),

        ("Module 3 — Real-Time Visual Slot Display (Python + JS)",
         "Data Structure: In-Memory 2D Matrix Array [O(1) lookup]\n\n"
         "Algorithm PushSlotDiff(slotId, status, plate):\n"
         "    matrix[row][col].status = status\n"
         "    matrix[row][col].plate = plate\n"
         "    WebSocket.emit(\"slot_state_changed\", {slotId, status, plate})"),

        ("Module 4 — Continuous Time Tracking (Python + C++)",
         "Data Structure: Hash Map (plate -> entry) + Min-Heap ordered by entry_time [O(1) peek]\n\n"
         "Algorithm DetectOverstay(threshold_minutes):\n"
         "    alerts = []\n"
         "    while TimeHeap.notEmpty() and (now() - TimeHeap.peek().entryTime) >= threshold_minutes:\n"
         "        rec = TimeHeap.pop()\n"
         "        if rec.active:\n"
         "            alerts.append(rec)\n"
         "    return alerts"),

        ("Module 5 — Tariff Engine & Fee Calculation (Java)",
         "Data Structure: Small Dynamic Tariff Lookup Table [O(1) scan]\n\n"
         "Algorithm CalculateFee(minutes):\n"
         "    m = max(0, minutes)\n"
         "    for tier in tariffTable:\n"
         "        if m <= tier.maxMinutes: return tier.fee\n"
         "    return 500.00"),

        ("Module 6 — Safaricom Daraja M-Pesa STK Push (Java / Spring Boot)",
         "Data Structure: FIFO Queue (ConcurrentLinkedQueue) for Webhook Payloads\n\n"
         "Algorithm DispatchSTK(sessionId, phone, fee):\n"
         "    pwd = Base64(Shortcode + Passkey + Timestamp(\"yyyyMMddHHmmss\"))\n"
         "    reqId = DarajaAPI.sendSTKPush(phone, fee, pwd)\n"
         "    pendingMap.put(reqId, {sessionId, fee, phone})\n"
         "    return reqId\n\n"
         "Algorithm OnWebhook(payload):\n"
         "    fifoQueue.offer(payload) // FIFO Queue\n"
         "    while not fifoQueue.isEmpty():\n"
         "        event = fifoQueue.poll()\n"
         "        if event.resultCode == 0:\n"
         "            MarkPaid(event.checkoutRequestId)\n"
         "            TriggerBarrierActuator(event.sessionId)\n"
         "            NotificationQueue.enqueue(event)"),

        ("Module 7 — Barrier Actuator Finite State Machine (C++)",
         "Data Structure: LIFO Stack (std::stack<BarrierLog>) for Safety Auditing\n\n"
         "Algorithm HandlePaymentConfirmed(sessionId):\n"
         "    if state == CLOSED or state == CLOSING:\n"
         "        state = OPENING\n"
         "        auditStack.push({transitionId++, from: \"CLOSED\", to: \"OPENING\", trigger: \"PAYMENT\"})\n"
         "        ActuatorHardware.open()\n"
         "        state = OPEN\n"
         "        return true\n"
         "    return false"),

        ("Module 8 — Relational Database Management (Python / SQLAlchemy)",
         "Data Structure: B-Tree Index on Timestamp & Foreign Keys; Repository Pattern\n\n"
         "Algorithm RepoWrite(modelInstance):\n"
         "    db = SessionLocal()\n"
         "    try: db.add(modelInstance); db.commit()\n"
         "    catch e: db.rollback(); raise e\n"
         "    finally: db.close()"),

        ("Module 9 — Admin Analytics & Reporting (Python)",
         "Data Structure: B-Tree Range Queries on Timestamps\n\n"
         "Algorithm QueryRevenue(start, end):\n"
         "    return DB.query(sum(fee_charged))\n"
         "             .filter(entry_time >= start, exit_time <= end, paid == True)"),

        ("Module 10 — Authentication & Role-Based Access Control (Python)",
         "Data Structure: Hash Map Active Sessions; Bcrypt Hash\n\n"
         "Algorithm Login(username, pass):\n"
         "    user = DB.find(username)\n"
         "    if user and bcrypt_verify(pass, user.hash):\n"
         "        session_token = uuid()\n"
         "        activeSessionMap[session_token] = user.role\n"
         "        return session_token"),

        ("Module 11 — Notification Dispatcher (Java / Spring Boot + Python)",
         "Data Structure: FIFO Queue (ConcurrentLinkedQueue) for SMS Receipts\n\n"
         "Algorithm EnqueueNotification(phone, receipt, amount):\n"
         "    job = {phone, receipt, amount, text: \"SmartPark KE: Confirmed Kshs \" + amount}\n"
         "    notifQueue.offer(job)\n"
         "    worker = notifQueue.poll()\n"
         "    AfricasTalking.sendSMS(worker.phone, worker.text)")
    ]

    for title, code in algos:
        story.append(Paragraph(title, h1_style))
        story.append(Paragraph(code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {pdf_path}")


if __name__ == "__main__":
    generate_docx()
    generate_system_documentation_pdf()
    generate_algorithms_pseudocode_pdf()
    print("All documentation generated successfully!")
