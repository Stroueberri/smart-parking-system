#ifndef BARRIER_STATE_MACHINE_H
#define BARRIER_STATE_MACHINE_H

#include <string>
#include <stack>
#include <vector>
#include <chrono>

/**
 * @enum BarrierState
 * @brief Discrete operational states of the physical gate actuator.
 */
enum class BarrierState {
    CLOSED,
    OPENING,
    OPEN,
    CLOSING
};

/**
 * @struct BarrierTransitionLog
 * @brief Record of an FSM transition for safety auditing.
 */
struct BarrierTransitionLog {
    int transitionId;
    std::string fromState;
    std::string toState;
    std::string trigger;       ///< e.g. "PAYMENT_CONFIRMED", "SENSOR_CLEARED", "TIMEOUT"
    int sessionId;
    std::string timestamp;
};

/**
 * @class BarrierStateMachine
 * @brief Actuator control state machine with LIFO audit log.
 *
 * Backs Module 7: Barrier Control Module.
 * Implements transitions:
 *  CLOSED -> OPENING (on payment confirmation)
 *  OPENING -> OPEN (actuator raised)
 *  OPEN -> CLOSING (on vehicle passage sensor or 10s timeout)
 *  CLOSING -> CLOSED (actuator lowered)
 *
 * Data Structure:
 *  std::stack<BarrierTransitionLog> (LIFO Stack) for O(1) push and inspection
 *  of the most recent operational events.
 *
 * Time Complexity:
 *  - Trigger transition: O(1)
 *  - Peek last transition: O(1)
 *  - Space Complexity: O(T) where T = total transitions
 */
class BarrierStateMachine {
private:
    BarrierState currentState;
    std::stack<BarrierTransitionLog> auditStack;
    int nextTransitionId;
    int autoCloseSeconds;

    std::string stateToString(BarrierState state) const;
    std::string getCurrentIsoTimestamp() const;

public:
    BarrierStateMachine(int autoCloseSec = 10);
    ~BarrierStateMachine();

    /**
     * @brief Transitions barrier to OPENING after payment verification.
     * @param sessionId Parking session ID granting exit.
     * @return true if state transitioned successfully.
     */
    bool handlePaymentConfirmed(int sessionId);

    /**
     * @brief Completes mechanical opening to OPEN state.
     */
    bool handleFullyOpened();

    /**
     * @brief Triggers closing when vehicle passage sensor trips or timeout expires.
     * @param triggerReason "VEHICLE_SENSOR" or "TIMEOUT".
     */
    bool handleVehiclePassedOrTimeout(const std::string& triggerReason = "VEHICLE_SENSOR");

    /**
     * @brief Completes mechanical closing to CLOSED state.
     */
    bool handleFullyClosed();

    /**
     * @brief Emergency / manual operator override to any valid state.
     */
    bool forceState(BarrierState newState, const std::string& operatorReason);

    /**
     * @brief Returns current FSM state name.
     */
    std::string getStateName() const;

    /**
     * @brief Inspects the most recent state transition (top of LIFO stack).
     * @complexity O(1)
     */
    BarrierTransitionLog peekRecentLog() const;

    /**
     * @brief Returns copy of the audit trail in chronological or reverse order.
     */
    std::vector<BarrierTransitionLog> getRecentLogs(size_t limit = 20) const;

    /**
     * @brief Returns configured auto-close timeout in seconds.
     */
    int getAutoCloseSeconds() const;
};

#endif // BARRIER_STATE_MACHINE_H
