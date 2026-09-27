#ifndef MIN_HEAP_H
#define MIN_HEAP_H

#include <vector>
#include <string>
#include <stdexcept>
#include <iostream>

/**
 * @struct SlotNode
 * @brief Represents a parking slot with its geometric distance and status.
 */
struct SlotNode {
    int slotId;
    std::string slotLabel;
    int zoneId;
    double distance;    ///< Distance from entrance in meters (priority key)
    int row;
    int col;
    std::string vehicleType;

    bool operator>(const SlotNode& other) const {
        return distance > other.distance;
    }

    bool operator<(const SlotNode& other) const {
        return distance < other.distance;
    }
};

/**
 * @class MinHeap
 * @brief Custom binary Min-Heap priority queue for parking slot allocation.
 *
 * Backs Module 2: Nearest Slot Allocation Engine.
 * Time Complexity:
 *  - Insert (push): O(log n)
 *  - Extract Min (pop): O(log n)
 *  - Peek Min: O(1)
 *  - Space Complexity: O(n)
 */
class MinHeap {
private:
    std::vector<SlotNode> heap;

    int parent(int i) const { return (i - 1) / 2; }
    int leftChild(int i) const { return 2 * i + 1; }
    int rightChild(int i) const { return 2 * i + 2; }

    void siftUp(int i);
    void siftDown(int i);

public:
    MinHeap();
    ~MinHeap();

    /**
     * @brief Inserts a free parking slot into the heap.
     * @param slot SlotNode containing slot metadata and distance.
     * @complexity O(log n)
     */
    void insert(const SlotNode& slot);

    /**
     * @brief Extracts and removes the closest free parking slot.
     * @return SlotNode with minimum distance.
     * @throws std::runtime_error if heap is empty.
     * @complexity O(log n)
     */
    SlotNode extractMin();

    /**
     * @brief Inspects the closest free parking slot without removing it.
     * @return Const reference to closest SlotNode.
     * @complexity O(1)
     */
    const SlotNode& peekMin() const;

    /**
     * @brief Checks if heap has no available slots.
     * @return true if empty, false otherwise.
     */
    bool isEmpty() const;

    /**
     * @brief Returns current count of free slots in heap.
     * @return size_t number of items.
     */
    size_t size() const;

    /**
     * @brief Clears all slots from the heap.
     */
    void clear();

    /**
     * @brief Returns a copy of all current elements for serialization.
     */
    std::vector<SlotNode> getElements() const;
};

#endif // MIN_HEAP_H
