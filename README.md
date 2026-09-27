# SmartPark KE — Intelligent Automated Parking Management System

The complete implementation and deliverables for **SmartPark KE** are organized in the [`smartpark-ke/`](./smartpark-ke/) directory, matching the exact repository specification:

```
smartpark-ke/
├── README.md
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── SmartPark_KE_System_Documentation.docx
│   ├── SmartPark_KE_System_Documentation.pdf
│   ├── ERD_diagram.png
│   ├── architecture_diagram.png
│   └── algorithms_pseudocode.pdf
├── web-gateway-python/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── templates/
│   ├── static/
│   ├── sockets/
│   ├── requirements.txt
│   └── tests/
├── slot-engine-cpp/
│   ├── src/
│   │   ├── main.cpp
│   │   ├── MinHeap.cpp / .h
│   │   ├── Graph.cpp / .h
│   │   ├── DoublyLinkedList.cpp / .h
│   │   └── BarrierStateMachine.cpp / .h
│   ├── CMakeLists.txt
│   └── tests/
├── billing-payment-java/
│   ├── src/main/java/com/smartpark/billing/
│   │   ├── FeeCalculator.java
│   │   ├── MpesaStkPushService.java
│   │   ├── PaymentCallbackController.java
│   │   └── NotificationDispatcher.java
│   ├── pom.xml
│   └── src/test/java/
├── database/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── migrations/
└── .github/workflows/ci.yml
```

### Quick Run
```bash
cd smartpark-ke
pip install -r web-gateway-python/requirements.txt
python web-gateway-python/app.py
```
Open [http://localhost:5000](http://localhost:5000) to view the live system.
Run tests:
```bash
pytest smartpark-ke/web-gateway-python/tests/test_api.py -v
```
All documentation (DOCX, PDF, Architecture & ERD diagrams) is inside [`smartpark-ke/docs/`](./smartpark-ke/docs/).
