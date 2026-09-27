#include "BarrierStateMachine.h"
#include <iomanip>
#include <sstream>
#include <ctime>

BarrierStateMachine::BarrierStateMachine(int autoCloseSec)
    : currentState(BarrierState::CLOSED), nextTransitionId(1), autoCloseSeconds(autoCloseSec) {
    // Initial audit log
    BarrierTransitionLog initialLog;
    initialLog.transitionId = nextTransitionId++;
    initialLog.fromState = "INITIAL";
    initialLog.toState = "CLOSED";
    initialLog.trigger = "SYSTEM_STARTUP";
    initialLog.sessionId = 0;
    initialLog.timestamp = getCurrentIsoTimestamp();
    auditStack.push(initialLog);
}

BarrierStateMachine::~BarrierStateMachine() {}

std::string BarrierStateMachine::stateToString(BarrierState state) const {
    switch (state) {
        case BarrierState::CLOSED: return "CLOSED";
        case BarrierState::OPENING: return "OPENING";
        case BarrierState::OPEN: return "OPEN";
        case BarrierState::CLOSING: return "CLOSING";
        default: return "UNKNOWN";
    }
}

std::string BarrierStateMachine::getCurrentIsoTimestamp() const {
    auto now = std::chrono::system_clock::now();
    std::time_t now_c = std::chrono::system_clock::to_time_t(now);
    std::tm now_tm;
#if defined(_WIN32) || defined(_WIN64)
    localtime_s(&now_tm, &now_c);
#else
    localtime_r(&now_c, &now_tm);
#endif
    std::ostringstream ss;
    ss << std::put_time(&now_tm, "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

bool BarrierStateMachine::handlePaymentConfirmed(int sessionId) {
    if (currentState == BarrierState::CLOSED || currentState == BarrierState::CLOSING) {
        BarrierTransitionLog log;
        log.transitionId = nextTransitionId++;
        log.fromState = stateToString(currentState);
        log.toState = "OPENING";
        log.trigger = "PAYMENT_CONFIRMED";
        log.sessionId = sessionId;
        log.timestamp = getCurrentIsoTimestamp();

        currentState = BarrierState::OPENING;
        auditStack.push(log); // O(1) push to LIFO audit stack
        return true;
    }
    return false;
}

bool BarrierStateMachine::handleFullyOpened() {
    if (currentState == BarrierState::OPENING) {
        BarrierTransitionLog log;
        log.transitionId = nextTransitionId++;
        log.fromState = "OPENING";
        log.toState = "OPEN";
        log.trigger = "ACTUATOR_LIMIT_SWITCH";
        log.sessionId = auditStack.empty() ? 0 : auditStack.top().sessionId;
        log.timestamp = getCurrentIsoTimestamp();

        currentState = BarrierState::OPEN;
        auditStack.push(log);
        return true;
    }
    return false;
}

bool BarrierStateMachine::handleVehiclePassedOrTimeout(const std::string& triggerReason) {
    if (currentState == BarrierState::OPEN) {
        BarrierTransitionLog log;
        log.transitionId = nextTransitionId++;
        log.fromState = "OPEN";
        log.toState = "CLOSING";
        log.trigger = triggerReason; // "VEHICLE_SENSOR" or "TIMEOUT"
        log.sessionId = auditStack.empty() ? 0 : auditStack.top().sessionId;
        log.timestamp = getCurrentIsoTimestamp();

        currentState = BarrierState::CLOSING;
        auditStack.push(log);
        return true;
    }
    return false;
}

bool BarrierStateMachine::handleFullyClosed() {
    if (currentState == BarrierState::CLOSING) {
        BarrierTransitionLog log;
        log.transitionId = nextTransitionId++;
        log.fromState = "CLOSING";
        log.toState = "CLOSED";
        log.trigger = "GATE_DOWN_SENSOR";
        log.sessionId = auditStack.empty() ? 0 : auditStack.top().sessionId;
        log.timestamp = getCurrentIsoTimestamp();

        currentState = BarrierState::CLOSED;
        auditStack.push(log);
        return true;
    }
    return false;
}

bool BarrierStateMachine::forceState(BarrierState newState, const std::string& operatorReason) {
    BarrierTransitionLog log;
    log.transitionId = nextTransitionId++;
    log.fromState = stateToString(currentState);
    log.toState = stateToString(newState);
    log.trigger = "MANUAL_OVERRIDE: " + operatorReason;
    log.sessionId = 0;
    log.timestamp = getCurrentIsoTimestamp();

    currentState = newState;
    auditStack.push(log);
    return true;
}

std::string BarrierStateMachine::getStateName() const {
    return stateToString(currentState);
}

BarrierTransitionLog BarrierStateMachine::peekRecentLog() const {
    if (auditStack.empty()) {
        throw std::runtime_error("Audit stack is empty");
    }
    return auditStack.top(); // O(1) LIFO inspection
}

std::vector<BarrierTransitionLog> BarrierStateMachine::getRecentLogs(size_t limit) const {
    std::vector<BarrierTransitionLog> logs;
    std::stack<BarrierTransitionLog> temp = auditStack;
    while (!temp.empty() && logs.size() < limit) {
        logs.push_back(temp.top());
        temp.pop();
    }
    return logs;
}

int BarrierStateMachine::getAutoCloseSeconds() const {
    return autoCloseSeconds;
}
