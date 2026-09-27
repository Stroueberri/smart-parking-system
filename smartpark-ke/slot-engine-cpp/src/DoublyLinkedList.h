#ifndef DOUBLY_LINKED_LIST_H
#define DOUBLY_LINKED_LIST_H

#include <string>
#include <vector>
#include <unordered_map>
#include <stdexcept>

/**
 * @struct DllSlotNode
 * @brief Node in the row doubly linked list representing a physical parking bay.
 */
struct DllSlotNode {
    int slotId;
    std::string slotLabel;
    int colPosition;
    std::string status;       ///< "FREE", "OCCUPIED", "RESERVED"
    double distance;
    DllSlotNode* prev;
    DllSlotNode* next;

    DllSlotNode(int id, const std::string& label, int col, const std::string& st, double dist)
        : slotId(id), slotLabel(label), colPosition(col), status(st), distance(dist), prev(nullptr), next(nullptr) {}
};

/**
 * @class RowDoublyLinkedList
 * @brief Doubly Linked List maintaining the physical ordering of parking bays in a row/zone.
 *
 * Backs Module 2 & 3:
 * Enables O(1) status transitions and O(1) re-insertion relative to physical neighbor nodes,
 * ensuring the visual slot display mirrors the real physical bay ordering.
 *
 * Time Complexity:
 *  - Insert after/before neighbor: O(1)
 *  - Update status by slotId: O(1) via auxiliary hash lookup
 *  - Traverse row for visual render: O(k) where k = bays in row
 *  - Space Complexity: O(k)
 */
class RowDoublyLinkedList {
private:
    DllSlotNode* head;
    DllSlotNode* tail;
    size_t count;
    std::unordered_map<int, DllSlotNode*> slotMap; ///< O(1) node lookup

public:
    RowDoublyLinkedList();
    ~RowDoublyLinkedList();

    /**
     * @brief Appends a slot at the end of the row.
     */
    void append(int slotId, const std::string& label, int colPosition, const std::string& status, double distance);

    /**
     * @brief Inserts a freed/new slot immediately after a designated neighbor.
     * @param neighborSlotId ID of existing bay in row.
     * @param newSlotId ID of new/re-inserted bay.
     * @complexity O(1)
     */
    void insertAfter(int neighborSlotId, int newSlotId, const std::string& label, int colPosition, const std::string& status, double distance);

    /**
     * @brief Updates status of a parking slot in O(1) time.
     * @param slotId Slot identifier.
     * @param newStatus "FREE", "OCCUPIED", "RESERVED".
     * @return true if found and updated.
     */
    bool updateStatus(int slotId, const std::string& newStatus);

    /**
     * @brief Retrieves node pointer by slot ID in O(1).
     */
    DllSlotNode* findSlot(int slotId) const;

    /**
     * @brief Returns snapshot of all slots in physical column order.
     */
    std::vector<DllSlotNode> getOrderedSlots() const;

    /**
     * @brief Total count of bays in row.
     */
    size_t size() const;

    /**
     * @brief Deallocates all list nodes.
     */
    void clear();
};

#endif // DOUBLY_LINKED_LIST_H
