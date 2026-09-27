#include <iostream>
#include <cassert>
#include <vector>
#include <string>
#include "../src/MinHeap.h"
#include "../src/Graph.h"
#include "../src/DoublyLinkedList.h"
#include "../src/BarrierStateMachine.h"

void testMinHeap() {
    std::cout << "[RUNNING] testMinHeap..." << std::endl;
    MinHeap heap;
    assert(heap.isEmpty());
    assert(heap.size() == 0);

    SlotNode s1{1, "A1", 1, 15.5, 1, 1, "car"};
    SlotNode s2{2, "A2", 1, 5.0, 1, 2, "car"};
    SlotNode s3{3, "A3", 1, 22.0, 1, 3, "car"};
    SlotNode s4{4, "A4", 1, 8.2, 1, 4, "car"};

    heap.insert(s1);
    heap.insert(s2);
    heap.insert(s3);
    heap.insert(s4);

    assert(!heap.isEmpty());
    assert(heap.size() == 4);

    // Closest slot must be s2 (distance 5.0)
    assert(heap.peekMin().slotLabel == "A2");
    SlotNode min1 = heap.extractMin();
    assert(min1.slotLabel == "A2");
    assert(min1.distance == 5.0);

    // Next closest must be s4 (distance 8.2)
    SlotNode min2 = heap.extractMin();
    assert(min2.slotLabel == "A4");

    // Next closest must be s1 (distance 15.5)
    SlotNode min3 = heap.extractMin();
    assert(min3.slotLabel == "A1");

    // Final must be s3 (distance 22.0)
    SlotNode min4 = heap.extractMin();
    assert(min4.slotLabel == "A3");

    assert(heap.isEmpty());
    std::cout << "[PASSED] testMinHeap" << std::endl;
}

void testGraphAndDijkstra() {
    std::cout << "[RUNNING] testGraphAndDijkstra..." << std::endl;
    ParkingGraph graph;

    // Build multi-zone graph
    graph.addNode(0, "ENTRANCE");
    graph.addNode(1, "JUNCTION_A");
    graph.addNode(2, "JUNCTION_B");
    graph.addNode(3, "SLOT_A1");
    graph.addNode(4, "SLOT_B1");

    graph.addEdge(0, 1, 10.0);
    graph.addEdge(0, 2, 25.0);
    graph.addEdge(1, 3, 5.0);   // path 0 -> 1 -> 3 total = 15.0
    graph.addEdge(2, 4, 5.0);   // path 0 -> 2 -> 4 total = 30.0
    graph.addEdge(1, 2, 8.0);   // alternate shortcut 0 -> 1 -> 2 -> 4 total = 10+8+5 = 23.0

    PathResult res = graph.dijkstra(0);

    assert(res.distances[0] == 0.0);
    assert(res.distances[1] == 10.0);
    assert(res.distances[3] == 15.0);
    // Shortcut via junction 1 to junction 2 (10 + 8 = 18 < 25)
    assert(res.distances[2] == 18.0);
    // Destination 4 distance: 18 + 5 = 23
    assert(res.distances[4] == 23.0);

    std::vector<int> path = graph.reconstructPath(res.predecessors, 4);
    assert(path.size() == 4);
    assert(path[0] == 0 && path[1] == 1 && path[2] == 2 && path[3] == 4);

    std::cout << "[PASSED] testGraphAndDijkstra" << std::endl;
}

void testDoublyLinkedList() {
    std::cout << "[RUNNING] testDoublyLinkedList..." << std::endl;
    RowDoublyLinkedList row;
    assert(row.size() == 0);

    row.append(1, "A1", 1, "FREE", 5.0);
    row.append(2, "A2", 2, "FREE", 8.5);
    row.append(3, "A3", 3, "FREE", 12.0);

    assert(row.size() == 3);
    assert(row.findSlot(2) != nullptr);
    assert(row.findSlot(2)->slotLabel == "A2");

    // O(1) status update
    bool updated = row.updateStatus(2, "OCCUPIED");
    assert(updated);
    assert(row.findSlot(2)->status == "OCCUPIED");

    // O(1) neighbor insertion: insert A1_TEMP after A1
    row.insertAfter(1, 99, "A1_TEMP", 1, "RESERVED", 6.0);
    assert(row.size() == 4);

    auto slots = row.getOrderedSlots();
    assert(slots.size() == 4);
    assert(slots[0].slotId == 1);
    assert(slots[1].slotId == 99);
    assert(slots[2].slotId == 2);
    assert(slots[3].slotId == 3);

    std::cout << "[PASSED] testDoublyLinkedList" << std::endl;
}

void testBarrierStateMachine() {
    std::cout << "[RUNNING] testBarrierStateMachine..." << std::endl;
    BarrierStateMachine fsm(10);

    assert(fsm.getStateName() == "CLOSED");
    BarrierTransitionLog initLog = fsm.peekRecentLog();
    assert(initLog.toState == "CLOSED");

    // Payment confirmation transitions to OPENING
    bool pOk = fsm.handlePaymentConfirmed(501);
    assert(pOk);
    assert(fsm.getStateName() == "OPENING");
    assert(fsm.peekRecentLog().toState == "OPENING");
    assert(fsm.peekRecentLog().sessionId == 501);

    // Gate reaches limit switch -> OPEN
    bool openOk = fsm.handleFullyOpened();
    assert(openOk);
    assert(fsm.getStateName() == "OPEN");
    assert(fsm.peekRecentLog().toState == "OPEN");

    // Vehicle sensor detects passage -> CLOSING
    bool passOk = fsm.handleVehiclePassedOrTimeout("VEHICLE_SENSOR");
    assert(passOk);
    assert(fsm.getStateName() == "CLOSING");

    // Gate down sensor -> CLOSED
    bool closeOk = fsm.handleFullyClosed();
    assert(closeOk);
    assert(fsm.getStateName() == "CLOSED");

    // Check LIFO audit stack history depth
    auto logs = fsm.getRecentLogs(10);
    assert(logs.size() >= 5);
    // Top of stack is most recent
    assert(logs[0].toState == "CLOSED");
    assert(logs[1].toState == "CLOSING");
    assert(logs[2].toState == "OPEN");

    std::cout << "[PASSED] testBarrierStateMachine" << std::endl;
}

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "  SmartPark KE — C++ Unit Test Suite    " << std::endl;
    std::cout << "========================================" << std::endl;

    testMinHeap();
    testGraphAndDijkstra();
    testDoublyLinkedList();
    testBarrierStateMachine();

    std::cout << "========================================" << std::endl;
    std::cout << "  ALL C++ UNIT TESTS PASSED SUCCESSFULLY! " << std::endl;
    std::cout << "========================================" << std::endl;
    return 0;
}
