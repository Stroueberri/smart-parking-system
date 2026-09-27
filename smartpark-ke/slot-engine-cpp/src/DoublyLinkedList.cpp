#include "DoublyLinkedList.h"

RowDoublyLinkedList::RowDoublyLinkedList() : head(nullptr), tail(nullptr), count(0) {}

RowDoublyLinkedList::~RowDoublyLinkedList() {
    clear();
}

void RowDoublyLinkedList::clear() {
    DllSlotNode* curr = head;
    while (curr != nullptr) {
        DllSlotNode* next = curr->next;
        delete curr;
        curr = next;
    }
    head = nullptr;
    tail = nullptr;
    count = 0;
    slotMap.clear();
}

void RowDoublyLinkedList::append(int slotId, const std::string& label, int colPosition, const std::string& status, double distance) {
    DllSlotNode* newNode = new DllSlotNode(slotId, label, colPosition, status, distance);
    if (!head) {
        head = tail = newNode;
    } else {
        tail->next = newNode;
        newNode->prev = tail;
        tail = newNode;
    }
    slotMap[slotId] = newNode;
    count++;
}

void RowDoublyLinkedList::insertAfter(int neighborSlotId, int newSlotId, const std::string& label, int colPosition, const std::string& status, double distance) {
    auto it = slotMap.find(neighborSlotId);
    if (it == slotMap.end()) {
        append(newSlotId, label, colPosition, status, distance);
        return;
    }

    DllSlotNode* prevNode = it->second;
    DllSlotNode* newNode = new DllSlotNode(newSlotId, label, colPosition, status, distance);

    newNode->next = prevNode->next;
    newNode->prev = prevNode;

    if (prevNode->next != nullptr) {
        prevNode->next->prev = newNode;
    } else {
        tail = newNode;
    }
    prevNode->next = newNode;

    slotMap[newSlotId] = newNode;
    count++;
}

bool RowDoublyLinkedList::updateStatus(int slotId, const std::string& newStatus) {
    auto it = slotMap.find(slotId);
    if (it != slotMap.end()) {
        it->second->status = newStatus;
        return true;
    }
    return false;
}

DllSlotNode* RowDoublyLinkedList::findSlot(int slotId) const {
    auto it = slotMap.find(slotId);
    if (it != slotMap.end()) {
        return it->second;
    }
    return nullptr;
}

std::vector<DllSlotNode> RowDoublyLinkedList::getOrderedSlots() const {
    std::vector<DllSlotNode> slots;
    slots.reserve(count);
    DllSlotNode* curr = head;
    while (curr != nullptr) {
        slots.push_back(*curr);
        curr = curr->next;
    }
    return slots;
}

size_t RowDoublyLinkedList::size() const {
    return count;
}
