"""
SmartPark KE — Time Tracking Module
Module 4: Time Tracking & Overstay Detection

Data Structures:
 1. Hash Map (plate_number -> StayRecord): O(1) duration lookups and active status checks.
 2. Min-Heap ordered by entry_time: O(1) peek at oldest entry / longest-staying vehicle,
    allowing overstay detection without linear O(N) table scans.
"""

import heapq
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class StayRecord:
    def __init__(self, session_id: int, plate_number: str, slot_label: str, entry_time: datetime):
        self.session_id = session_id
        self.plate_number = plate_number.upper().strip()
        self.slot_label = slot_label
        self.entry_time = entry_time
        self.active = True

    @property
    def elapsed_minutes(self) -> int:
        now = datetime.utcnow()
        delta = now - self.entry_time
        return max(0, int(delta.total_seconds() // 60))

    def __lt__(self, other: "StayRecord") -> bool:
        # Min-Heap ordering: earlier entry_time means vehicle has been parked LONGEST
        return self.entry_time < other.entry_time


class TimeTracker:
    def __init__(self):
        # Hash Map: plate_number -> StayRecord (O(1) lookup)
        self.plate_map: Dict[str, StayRecord] = {}
        # Min-Heap: stores (entry_time, StayRecord)
        self.entry_heap: List[StayRecord] = []

    def record_entry(self, session_id: int, plate_number: str, slot_label: str, entry_time: Optional[datetime] = None) -> StayRecord:
        """
        Registers vehicle arrival in O(log n) time.
        """
        if entry_time is None:
            entry_time = datetime.utcnow()
        clean_plate = plate_number.upper().strip()

        record = StayRecord(session_id, clean_plate, slot_label, entry_time)
        self.plate_map[clean_plate] = record
        heapq.heappush(self.entry_heap, record)
        return record

    def record_exit(self, plate_number: str) -> Optional[StayRecord]:
        """
        Marks vehicle as exited in O(1) time.
        """
        clean_plate = plate_number.upper().strip()
        record = self.plate_map.pop(clean_plate, None)
        if record:
            record.active = False
        return record

    def get_stay_record(self, plate_number: str) -> Optional[StayRecord]:
        """
        O(1) active vehicle session lookup.
        """
        return self.plate_map.get(plate_number.upper().strip())

    def get_elapsed_minutes(self, plate_number: str) -> Optional[int]:
        """
        Computes elapsed parking duration in minutes in O(1) time.
        """
        record = self.get_stay_record(plate_number)
        return record.elapsed_minutes if record else None

    def get_longest_parked_vehicles(self, limit: int = 5) -> List[Dict]:
        """
        Returns top longest parked vehicles using the Min-Heap.
        Prunes inactive records lazily from the top of the heap.
        """
        results = []
        temp_popped = []

        while self.entry_heap and len(results) < limit:
            top = heapq.heappop(self.entry_heap)
            if top.active and top.plate_number in self.plate_map:
                results.append({
                    "sessionId": top.session_id,
                    "plateNumber": top.plate_number,
                    "slotLabel": top.slot_label,
                    "entryTime": top.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "durationMinutes": top.elapsed_minutes
                })
                temp_popped.append(top)
            # If not active, it's discarded (lazy cleanup)

        # Restore popped active items to heap
        for item in temp_popped:
            heapq.heappush(self.entry_heap, item)

        return results

    def get_overstay_vehicles(self, threshold_minutes: int = 360) -> List[Dict]:
        """
        Module 9: Overstay alerts (e.g. vehicles parked over 6 hours).
        Extracts all candidates exceeding threshold from the Min-Heap.
        """
        longest = self.get_longest_parked_vehicles(limit=50)
        return [v for v in longest if v["durationMinutes"] >= threshold_minutes]


# Global in-memory instance
tracker = TimeTracker()
