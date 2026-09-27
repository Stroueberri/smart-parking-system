# SmartPark KE — Intelligent Automated Parking Management System

[![CI Pipeline](https://github.com/smartpark-ke/smartpark-ke/actions/workflows/ci.yml/badge.svg)](https://github.com/smartpark-ke/smartpark-ke/actions)
[![Language: Polyglot](https://img.shields.io/badge/Language-Python%20%7C%20C%2B%2B%20%7C%20Java-blue.svg)](https://github.com/smartpark-ke/smartpark-ke)
[![Daraja M-Pesa](https://img.shields.io/badge/Payment-Safaricom%20M--Pesa%20STK%20Push-008751.svg)](https://developer.safaricom.co.ke/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An industrial-grade, polyglot microservice parking management system engineered for automated operations in Kenya. Implements real-time visual parking bay guidance, automated entry registration, dynamic tariff computation, Safaricom Daraja Lipa na M-Pesa STK push checkout, barrier actuator state machine simulation, and operational analytics.

---

## 1. System Overview & Architecture

SmartPark KE strictly divides engineering responsibilities across three programming languages according to their architectural strengths:

```
                         ┌─────────────────────────────┐
                         │   BROWSER (Driver / Admin)  │
                         │ HTML5 + CSS3 + JS + Chart.js│
                         │ Real-time slot map dashboard│
                         └──────────────┬──────────────┘
                                        │ REST/HTTPS + WebSocket (/ws/slots)
                         ┌──────────────▼──────────────┐
                         │  PYTHON — API GATEWAY / WEB │
                         │ (Flask 3 + Flask-SocketIO)  │
                         │ - Serves web interfaces     │
                         │ - Vehicle entry/exit logic  │
                         │ - TimeTracker Min-Heap/Map  │
                         │ - SQLAlchemy ORM Repository │
                         └──────┬──────────────┬───────┘
                                │ REST         │ REST
                  ┌─────────────▼───┐    ┌─────▼──────────────┐
                  │   C++ ENGINE    │    │    JAVA BILLING    │
                  │ Slot Allocation │    │ & PAYMENT SERVICE  │
                  │ & Barrier Logic │    │   (Spring Boot 3)  │
                  │ - Min-Heap      │    │ - Fee calculation  │
                  │ - Weighted Graph│    │ - Daraja STK Push  │
                  │   + Dijkstra    │    │ - FIFO Callback Q  │
                  │ - Doubly Linked │    │ - SMS Dispatcher   │
                  │   List (rows)   │    │ - Barrier trigger  │
                  │ - FSM + LIFO    │    └─────────┬──────────┘
                  │   Audit Stack   │              │
                  └─────────────────┘     ┌────────▼─────────┐
                                          │ Relational DB    │
                                          │ PostgreSQL/MySQL │
                                          └──────────────────┘
```

- **C++17 Engine (`slot-engine-cpp`)** — Performance-critical in-memory slot allocation and barrier control. Exposes a lightweight REST service (`:8081`).
- **Java 17 Service (`billing-payment-java`)** — Transactional billing, Safaricom Daraja M-Pesa STK Push, FIFO asynchronous webhook processing, and notification dispatch (`:8082`).
- **Python 3.11 Gateway (`web-gateway-python`)** — High-productivity API gateway, WebSocket live diffs, session tracking, relational persistence, and Chart.js reporting (`:5000`).

---

## 2. All 11 Functional Modules

| Module | Role | Primary Language | Underlying Data Structure | Complexity |
|---|---|---|---|---|
| **Module 1** | Vehicle Entry & Registration | Python + C++ | Hash Map `<plate, Session>` | O(1) duplicate prevention |
| **Module 2** | Nearest Slot Allocation Engine | C++ | Min-Heap + Graph Dijkstra + Doubly Linked List | O(log n) slot allocation; O((V+E)log V) multi-floor shortest path; O(1) row bay sync |
| **Module 3** | Real-Time Visual Slot Display | Python + JS | In-Memory 2D Matrix Array | O(1) cell access; WebSocket diff push |
| **Module 4** | Continuous Time Tracking | Python + C++ | Hash Map + Min-Heap (ordered by `entry_time`) | O(1) elapsed lookup; O(1) longest-stay overstay peek |
| **Module 5** | Fee Calculation & Tariff Engine | Java | Dynamic Tariff Lookup Array / Table | O(1) linear scan through 5 fixed tiers |
| **Module 6** | Payment Module: M-Pesa STK Push | Java (Spring Boot) | FIFO Queue (`ConcurrentLinkedQueue`) + Hash Map | O(1) callback enqueuing; O(1) `CheckoutRequestID` matching |
| **Module 7** | Barrier Control & Actuator FSM | C++ | LIFO Stack (`std::stack<BarrierLog>`) | O(1) FSM state transitions & audit trail inspection |
| **Module 8** | Database Management Module | Python (SQLAlchemy) | B-Tree Index on timestamps & foreign keys | Repository pattern isolating SQL writes |
| **Module 9** | Admin Analytics & Reporting | Python | B-Tree timestamp range queries | Aggregated revenue, occupancy rate, overstay alerts |
| **Module 10** | Authentication & RBAC | Python | Hash Map active sessions / JWT; Bcrypt | O(1) role and session validation |
| **Module 11** | Outbound Notification Module | Java / Python | FIFO Queue for SMS / Email receipts | O(1) retry-safe dispatch (Africa's Talking format) |

---

## 3. Fixed Tariff Schedule (Kenya Shillings)

| Duration | Fee (Kshs) | Description |
|---|---|---|
| **Up to 30 minutes** | **FREE** | Grace period / quick pickup |
| **Up to 2 hours** | **Kshs 50.00** | Short stay |
| **Up to 4 hours** | **Kshs 100.00** | Standard stay |
| **Up to 6 hours** | **Kshs 300.00** | Extended stay |
| **Over 6 hours** | **Kshs 500.00** | Full day cap |

*Note: Tariffs are data-driven and dynamically configurable at runtime via the `tariffs` table without redeploying code.*

---

## 4. REST API Contract

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/slots` | Returns live 2D slot grid matrix with occupancy and distances |
| `POST` | `/api/entry` | Registers vehicle arrival, allocates nearest bay from C++ Min-Heap |
| `GET` / `POST` | `/api/exit/<plate>` | Computes elapsed stay, calculates fee via Java billing service |
| `POST` | `/api/payment/stk-push` | Triggers Lipa na M-Pesa Online STK prompt to customer phone |
| `POST` | `/api/payment/confirm-webhook` | Webhook confirming payment; signals barrier open & dispatches SMS |
| `POST` | `/api/barrier/open/<session_id>` | Actuator override to open barrier |
| `POST` | `/api/barrier/sensor-cleared` | Passage sensor signal closing barrier arm |
| `GET` | `/api/barrier/status` | Returns current barrier FSM state and LIFO audit stack top |
| `GET` | `/api/reports/revenue` | Aggregated revenue metrics and recent transaction logs |
| `GET` | `/api/reports/occupancy` | Real-time lot and per-zone occupancy metrics |
| `GET` | `/api/reports/overstay` | Overstay vehicle alerts (> 6 hours) via Min-Heap |
| `GET` / `POST` | `/api/tariffs` | Dynamic tariff table management |
| `WebSocket` | `/ws/slots` | Real-time push of slot state diffs and barrier events |

---

## 5. Quick Start & Execution

### Option A: Docker Compose (All Services in 1 Command)
```bash
git clone https://github.com/smartpark-ke/smartpark-ke.git
cd smartpark-ke
cp .env.example .env
docker-compose up --build
```

### Option B: Local Standalone Execution (Development Mode)

#### 1. Start Python Web Gateway
```bash
cd web-gateway-python
pip install -r requirements.txt
python app.py
```
*Access web interface at: `http://localhost:5000`*

#### 2. Run Test Suite
```bash
pytest web-gateway-python/tests/test_api.py -v
```

#### 3. Compile & Run C++ Slot Engine (Optional / Docker)
```bash
cd slot-engine-cpp
mkdir build && cd build
cmake ..
make
./test_slot_engine
./slot_engine 8081
```

#### 4. Compile & Run Java Billing Service (Optional / Docker)
```bash
cd billing-payment-java
mvn clean test
mvn spring-boot:run
```

---

## 6. End-to-End Walkthrough Demo

1. **Driver Arrival (`http://localhost:5000/`)**:
   - Driver views live visual grid: Zone A (Entrance), Zone B (West Wing), Zone C (Rooftop Deck).
   - Enters plate `KDA 101A` & clicks **"Register Arrival & Get Nearest Slot"**.
   - C++ Min-Heap pops closest slot (`A1`, distance 5.0m).
   - In-memory 2D Matrix updates; WebSocket diff turns bay `A1` RED with plate tag.
   - Entry barrier opens.

2. **Continuous Stay Tracking**:
   - `TimeTracker` records entry time in Hash Map & pushes to `entry_time` Min-Heap.
   - Live elapsed minutes reflect on bay cards.

3. **Checkout & Fee Calculation (`http://localhost:5000/attendant`)**:
   - Attendant looks up plate `KDA 101A`.
   - Elapsed duration is retrieved in O(1).
   - Java Billing Service computes fee based on dynamic tariff table.

4. **Safaricom Lipa na M-Pesa STK Push**:
   - Attendant enters mobile number (e.g. `0712345678`).
   - Java Service initiates Daraja STK Push with Base64 credentials.
   - Prompt arrives on phone; Attendant clicks **"Simulate Customer Enters PIN"** (or real Daraja webhook callback).

5. **Barrier Release & SMS Receipt**:
   - Daraja callback enqueues in FIFO Queue; verifies `ResultCode == 0`.
   - Gate actuator FSM transitions `CLOSED -> OPENING -> OPEN` (animated boom arm raises).
   - Outbound SMS receipt enqueued in Notification FIFO Queue.
   - Slot `A1` is freed in DB and re-inserted into C++ Min-Heap and Row DLL in O(log n).
   - Sensor trips on vehicle departure (`POST /api/barrier/sensor-cleared`); gate arm lowers to `CLOSED`.

6. **Admin Analytics (`http://localhost:5000/admin`)**:
   - Real-time revenue chart updates with collected fee.
   - Occupancy rate re-adjusts.
   - Barrier LIFO audit stack top displays recent transition.

---

## 7. Comprehensive Documentation (`docs/`)

The repository includes a dedicated `docs/` folder containing full technical reports:
- [SmartPark_KE_System_Documentation.docx](docs/SmartPark_KE_System_Documentation.docx) — Full professional Word report.
- [SmartPark_KE_System_Documentation.pdf](docs/SmartPark_KE_System_Documentation.pdf) — Comprehensive multi-page PDF document with embedded figures.
- [algorithms_pseudocode.pdf](docs/algorithms_pseudocode.pdf) — Complete pseudocode breakdown for all 11 modules.
- [architecture_diagram.png](docs/architecture_diagram.png) — High-resolution polyglot architecture diagram.
- [ERD_diagram.png](docs/ERD_diagram.png) — Relational Entity-Relationship Diagram with B-Tree indices.

---

## 8. License & Authorship
Built with pair programming by Google DeepMind Advanced Agentic Coding (Antigravity) for the SmartPark KE project. Released under the MIT License.
