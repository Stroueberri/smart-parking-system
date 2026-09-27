#include "MinHeap.h"
#include <algorithm>

MinHeap::MinHeap() {}

MinHeap::~MinHeap() {}

void MinHeap::siftUp(int i) {
    while (i > 0 && heap[i] < heap[parent(i)]) {
        std::swap(heap[i], heap[parent(i)]);
        i = parent(i);
    }
}

void MinHeap::siftDown(int i) {
    int minIndex = i;
    int left = leftChild(i);
    int right = rightChild(i);
    int n = static_cast<int>(heap.size());

    if (left < n && heap[left] < heap[minIndex]) {
        minIndex = left;
    }
    if (right < n && heap[right] < heap[minIndex]) {
        minIndex = right;
    }

    if (i != minIndex) {
        std::swap(heap[i], heap[minIndex]);
        siftDown(minIndex);
    }
}

void MinHeap::insert(const SlotNode& slot) {
    heap.push_back(slot);
    siftUp(static_cast<int>(heap.size()) - 1);
}

SlotNode MinHeap::extractMin() {
    if (heap.empty()) {
        throw std::runtime_error("MinHeap is empty: No available parking slots");
    }
    SlotNode minSlot = heap[0];
    heap[0] = heap.back();
    heap.pop_back();
    if (!heap.empty()) {
        siftDown(0);
    }
    return minSlot;
}

const SlotNode& MinHeap::peekMin() const {
    if (heap.empty()) {
        throw std::runtime_error("MinHeap is empty: No available parking slots");
    }
    return heap[0];
}

bool MinHeap::isEmpty() const {
    return heap.empty();
}

size_t MinHeap::size() const {
    return heap.size();
}

void MinHeap::clear() {
    heap.clear();
}

std::vector<SlotNode> MinHeap::getElements() const {
    return heap;
}
