#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <unordered_map>
#include <thread>
#include <mutex>
#include <chrono>
#include <cstring>

#ifdef _WIN32
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  typedef SOCKET SocketType;
  #define CLOSE_SOCKET(s) closesocket(s)
  #define IS_INVALID_SOCKET(s) ((s) == INVALID_SOCKET)
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <unistd.h>
  typedef int SocketType;
  #define CLOSE_SOCKET(s) close(s)
  #define IS_INVALID_SOCKET(s) ((s) < 0)
#endif

#include "MinHeap.h"
#include "Graph.h"
#include "DoublyLinkedList.h"
#include "BarrierStateMachine.h"

// Mutex for thread-safe access to lot state
std::mutex g_engineMutex;

// Global engine state
MinHeap g_freeSlotsHeap;
ParkingGraph g_lotGraph;
std::unordered_map<int, RowDoublyLinkedList> g_zoneRowLists; // zoneId -> Row list
std::unordered_map<int, SlotNode> g_allSlots;               // slotId -> SlotNode
BarrierStateMachine g_barrierFsm(10);                       // 10s auto-close

// Helper to extract JSON string value
std::string extractJsonField(const std::string& json, const std::string& field) {
    std::string key = "\"" + field + "\"";
    size_t pos = json.find(key);
    if (pos == std::string::npos) return "";
    pos = json.find(':', pos);
    if (pos == std::string::npos) return "";
    pos = json.find_first_not_of(" \t\n\r", pos + 1);
    if (pos == std::string::npos) return "";

    if (json[pos] == '\"') {
        size_t endPos = json.find('\"', pos + 1);
        if (endPos != std::string::npos) {
            return json.substr(pos + 1, endPos - pos - 1);
        }
    } else {
        size_t endPos = json.find_first_of(",}\n\r", pos);
        if (endPos != std::string::npos) {
            return json.substr(pos, endPos - pos);
        }
    }
    return "";
}

int extractJsonInt(const std::string& json, const std::string& field, int defaultVal = 0) {
    std::string val = extractJsonField(json, field);
    if (val.empty()) return defaultVal;
    try {
        return std::stoi(val);
    } catch (...) {
        return defaultVal;
    }
}

/**
 * @brief Initializes parking lot graph, heap, and physical row doubly-linked lists.
 */
void initializeEngineData() {
    std::lock_guard<std::mutex> lock(g_engineMutex);

    // Setup Graph nodes: 0 = Entrance Gate, 100 = Zone A junction, 200 = Zone B junction, 300 = Zone C ramp
    g_lotGraph.addNode(0, "MAIN_ENTRANCE");
    g_lotGraph.addNode(100, "ZONE_A_JUNCTION");
    g_lotGraph.addNode(200, "ZONE_B_JUNCTION");
    g_lotGraph.addNode(300, "ZONE_C_RAMP");

    g_lotGraph.addEdge(0, 100, 5.0);
    g_lotGraph.addEdge(100, 200, 20.0);
    g_lotGraph.addEdge(200, 300, 25.0);

    // Seed Zone A (10 slots)
    for (int i = 1; i <= 10; ++i) {
        double dist = 5.0 + (i - 1) * 3.5;
        SlotNode s{i, "A" + std::to_string(i), 1, dist, (i <= 5 ? 1 : 2), ((i - 1) % 5) + 1, "car"};
        g_allSlots[i] = s;
        g_freeSlotsHeap.insert(s);
        g_zoneRowLists[1].append(s.slotId, s.slotLabel, s.col, "FREE", s.distance);
        g_lotGraph.addNode(1000 + i, s.slotLabel);
        g_lotGraph.addEdge(100, 1000 + i, dist);
    }

    // Seed Zone B (10 slots)
    for (int i = 1; i <= 10; ++i) {
        int id = 10 + i;
        double dist = 25.0 + (i - 1) * 3.5;
        SlotNode s{id, "B" + std::to_string(i), 2, dist, (i <= 5 ? 1 : 2), ((i - 1) % 5) + 1, "car"};
        g_allSlots[id] = s;
        g_freeSlotsHeap.insert(s);
        g_zoneRowLists[2].append(s.slotId, s.slotLabel, s.col, "FREE", s.distance);
        g_lotGraph.addNode(2000 + i, s.slotLabel);
        g_lotGraph.addEdge(200, 2000 + i, dist - 20.0);
    }

    // Seed Zone C (10 slots, Upper Deck)
    for (int i = 1; i <= 10; ++i) {
        int id = 20 + i;
        double dist = 50.0 + (i - 1) * 3.5;
        SlotNode s{id, "C" + std::to_string(i), 3, dist, (i <= 5 ? 1 : 2), ((i - 1) % 5) + 1, "car"};
        g_allSlots[id] = s;
        g_freeSlotsHeap.insert(s);
        g_zoneRowLists[3].append(s.slotId, s.slotLabel, s.col, "FREE", s.distance);
        g_lotGraph.addNode(3000 + i, s.slotLabel);
        g_lotGraph.addEdge(300, 3000 + i, dist - 45.0);
    }

    std::cout << "[C++ Engine] Initialized: 30 slots across 3 zones. MinHeap size = "
              << g_freeSlotsHeap.size() << ", Graph vertices = " << g_lotGraph.nodeCount() << std::endl;
}

/**
 * @brief Constructs an HTTP 200/400/404 response.
 */
std::string buildHttpResponse(int statusCode, const std::string& contentType, const std::string& body) {
    std::string statusMsg = (statusCode == 200) ? "OK" : (statusCode == 404 ? "Not Found" : "Bad Request");
    std::ostringstream response;
    response << "HTTP/1.1 " << statusCode << " " << statusMsg << "\r\n";
    response << "Content-Type: " << contentType << "\r\n";
    response << "Content-Length: " << body.length() << "\r\n";
    response << "Access-Control-Allow-Origin: *\r\n";
    response << "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n";
    response << "Access-Control-Allow-Headers: Content-Type\r\n";
    response << "Connection: close\r\n\r\n";
    response << body;
    return response.str();
}

/**
 * @brief Handles an incoming HTTP connection.
 */
void handleClientConnection(SocketType clientSocket) {
    char buffer[4096];
    std::memset(buffer, 0, sizeof(buffer));

    int bytesRead = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    if (bytesRead <= 0) {
        CLOSE_SOCKET(clientSocket);
        return;
    }

    std::string request(buffer, bytesRead);
    std::istringstream reqStream(request);
    std::string method, uri, httpVersion;
    reqStream >> method >> uri >> httpVersion;

    if (method == "OPTIONS") {
        std::string res = buildHttpResponse(200, "text/plain", "");
        send(clientSocket, res.c_str(), static_cast<int>(res.length()), 0);
        CLOSE_SOCKET(clientSocket);
        return;
    }

    // Extract body if POST
    std::string body = "";
    size_t bodyPos = request.find("\r\n\r\n");
    if (bodyPos != std::string::npos) {
        body = request.substr(bodyPos + 4);
    }

    std::string responseStr;

    if (method == "GET" && uri == "/health") {
        responseStr = buildHttpResponse(200, "application/json", "{\"status\":\"UP\",\"service\":\"slot-engine-cpp\",\"version\":\"2.0\"}");
    }
    else if (method == "GET" && uri == "/api/slots") {
        std::lock_guard<std::mutex> lock(g_engineMutex);
        std::ostringstream json;
        json << "{\"success\":true,\"totalSlots\":" << g_allSlots.size() << ",\"freeSlotsCount\":" << g_freeSlotsHeap.size() << ",\"slots\":[";

        bool first = true;
        for (const auto& pair : g_allSlots) {
            if (!first) json << ",";
            first = false;
            const SlotNode& s = pair.second;
            DllSlotNode* dllNode = g_zoneRowLists[s.zoneId].findSlot(s.slotId);
            std::string st = (dllNode ? dllNode->status : "FREE");

            json << "{\"slotId\":" << s.slotId
                 << ",\"slotLabel\":\"" << s.slotLabel << "\""
                 << ",\"zoneId\":" << s.zoneId
                 << ",\"distance\":" << s.distance
                 << ",\"row\":" << s.row
                 << ",\"col\":" << s.col
                 << ",\"status\":\"" << st << "\"}";
        }
        json << "]}";
        responseStr = buildHttpResponse(200, "application/json", json.str());
    }
    else if (method == "POST" && uri == "/api/slots/allocate") {
        // Module 2: Nearest Slot Allocation via MinHeap O(log n)
        std::lock_guard<std::mutex> lock(g_engineMutex);
        if (g_freeSlotsHeap.isEmpty()) {
            responseStr = buildHttpResponse(400, "application/json", "{\"success\":false,\"error\":\"Parking lot is completely full\"}");
        } else {
            SlotNode allocated = g_freeSlotsHeap.extractMin(); // O(log n)
            // Update physical row DLL in O(1)
            g_zoneRowLists[allocated.zoneId].updateStatus(allocated.slotId, "OCCUPIED");

            std::ostringstream json;
            json << "{\"success\":true,\"message\":\"Slot allocated successfully\",\"slot\":{"
                 << "\"slotId\":" << allocated.slotId
                 << ",\"slotLabel\":\"" << allocated.slotLabel << "\""
                 << ",\"zoneId\":" << allocated.zoneId
                 << ",\"distance\":" << allocated.distance
                 << ",\"row\":" << allocated.row
                 << ",\"col\":" << allocated.col
                 << ",\"remainingFree\":" << g_freeSlotsHeap.size()
                 << "}}";
            responseStr = buildHttpResponse(200, "application/json", json.str());
        }
    }
    else if (method == "POST" && uri == "/api/slots/release") {
        // Module 2: Free slot re-insertion into MinHeap O(log n) and Row DLL O(1)
        int slotId = extractJsonInt(body, "slotId");
        std::lock_guard<std::mutex> lock(g_engineMutex);

        auto it = g_allSlots.find(slotId);
        if (it != g_allSlots.end()) {
            SlotNode s = it->second;
            g_freeSlotsHeap.insert(s); // O(log n)
            g_zoneRowLists[s.zoneId].updateStatus(s.slotId, "FREE"); // O(1)

            std::ostringstream json;
            json << "{\"success\":true,\"message\":\"Slot released\",\"slotId\":" << slotId
                 << ",\"remainingFree\":" << g_freeSlotsHeap.size() << "}";
            responseStr = buildHttpResponse(200, "application/json", json.str());
        } else {
            responseStr = buildHttpResponse(404, "application/json", "{\"success\":false,\"error\":\"Slot not found\"}");
        }
    }
    else if (method == "POST" && uri == "/api/barrier/trigger") {
        // Module 7: Barrier Control FSM + LIFO Stack Log
        std::string action = extractJsonField(body, "action");
        int sessionId = extractJsonInt(body, "sessionId", 0);
        std::lock_guard<std::mutex> lock(g_engineMutex);

        bool transitioned = false;
        if (action == "PAYMENT_CONFIRMED") {
            transitioned = g_barrierFsm.handlePaymentConfirmed(sessionId);
            if (transitioned) {
                // Actuator moves to OPEN
                g_barrierFsm.handleFullyOpened();
            }
        } else if (action == "SENSOR_CLEARED" || action == "TIMEOUT") {
            transitioned = g_barrierFsm.handleVehiclePassedOrTimeout(action);
            if (transitioned) {
                g_barrierFsm.handleFullyClosed();
            }
        } else if (action == "FORCE_OPEN") {
            transitioned = g_barrierFsm.forceState(BarrierState::OPEN, "MANUAL_GATE_OVERRIDE");
        } else if (action == "FORCE_CLOSE") {
            transitioned = g_barrierFsm.forceState(BarrierState::CLOSED, "MANUAL_GATE_OVERRIDE");
        }

        BarrierTransitionLog recent = g_barrierFsm.peekRecentLog();
        std::ostringstream json;
        json << "{\"success\":" << (transitioned ? "true" : "false")
             << ",\"currentState\":\"" << g_barrierFsm.getStateName() << "\""
             << ",\"lastTransition\":{"
             << "\"transitionId\":" << recent.transitionId
             << ",\"from\":\"" << recent.fromState << "\""
             << ",\"to\":\"" << recent.toState << "\""
             << ",\"trigger\":\"" << recent.trigger << "\""
             << ",\"sessionId\":" << recent.sessionId
             << ",\"timestamp\":\"" << recent.timestamp << "\"}}";
        responseStr = buildHttpResponse(200, "application/json", json.str());
    }
    else if (method == "GET" && uri == "/api/barrier/status") {
        std::lock_guard<std::mutex> lock(g_engineMutex);
        BarrierTransitionLog recent = g_barrierFsm.peekRecentLog();
        auto history = g_barrierFsm.getRecentLogs(10);

        std::ostringstream json;
        json << "{\"currentState\":\"" << g_barrierFsm.getStateName() << "\""
             << ",\"autoCloseSeconds\":" << g_barrierFsm.getAutoCloseSeconds()
             << ",\"auditStackTop\":{"
             << "\"from\":\"" << recent.fromState << "\""
             << ",\"to\":\"" << recent.toState << "\""
             << ",\"trigger\":\"" << recent.trigger << "\""
             << ",\"sessionId\":" << recent.sessionId
             << ",\"timestamp\":\"" << recent.timestamp << "\"}"
             << ",\"history\":[";

        for (size_t i = 0; i < history.size(); ++i) {
            if (i > 0) json << ",";
            json << "{\"id\":" << history[i].transitionId
                 << ",\"from\":\"" << history[i].fromState << "\""
                 << ",\"to\":\"" << history[i].toState << "\""
                 << ",\"trigger\":\"" << history[i].trigger << "\""
                 << ",\"time\":\"" << history[i].timestamp << "\"}";
        }
        json << "]}";
        responseStr = buildHttpResponse(200, "application/json", json.str());
    }
    else {
        responseStr = buildHttpResponse(404, "application/json", "{\"error\":\"Route not found\"}");
    }

    send(clientSocket, responseStr.c_str(), static_cast<int>(responseStr.length()), 0);
    CLOSE_SOCKET(clientSocket);
}

int main(int argc, char* argv[]) {
    int port = 8081;
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }

    std::cout << "==========================================================" << std::endl;
    std::cout << "  SmartPark KE — C++ Slot Engine & Barrier Actuator        " << std::endl;
    std::cout << "  Port: " << port << " | Language: C++17                    " << std::endl;
    std::cout << "==========================================================" << std::endl;

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "Failed to initialize Winsock" << std::endl;
        return 1;
    }
#endif

    initializeEngineData();

    SocketType serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (IS_INVALID_SOCKET(serverSocket)) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    int opt = 1;
#ifdef _WIN32
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));
#else
    setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    sockaddr_in serverAddr;
    std::memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(static_cast<unsigned short>(port));

    if (bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "Bind failed on port " << port << std::endl;
        CLOSE_SOCKET(serverSocket);
        return 1;
    }

    if (listen(serverSocket, 10) < 0) {
        std::cerr << "Listen failed" << std::endl;
        CLOSE_SOCKET(serverSocket);
        return 1;
    }

    std::cout << "[C++ Engine] HTTP REST server listening on http://0.0.0.0:" << port << std::endl;

    while (true) {
        sockaddr_in clientAddr;
        socklen_t clientLen = sizeof(clientAddr);
        SocketType clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &clientLen);

        if (IS_INVALID_SOCKET(clientSocket)) {
            continue;
        }

        std::thread clientThread(handleClientConnection, clientSocket);
        clientThread.detach();
    }

    CLOSE_SOCKET(serverSocket);
#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}
