/**
 * SmartPark KE — Driver Entrance Display JavaScript
 * Module 3: Real-Time Visual Slot Display & Module 1 Entry Registration
 */

let allSlots = [];
let activeZoneFilter = 'all';

// Initialize Socket.IO connection
const socket = io();

socket.on('connect', () => {
    console.log('[Socket.IO] Connected to SmartPark live gateway');
    socket.emit('join_display');
});

// Real-time slot state diff listener (Module 3)
socket.on('slot_state_changed', (diff) => {
    console.log('[WebSocket] Slot state diff received:', diff);
    // Update local state
    const slotIdx = allSlots.findIndex(s => s.slotId === diff.slotId);
    if (slotIdx !== -1) {
        allSlots[slotIdx].status = diff.status;
        allSlots[slotIdx].currentPlate = diff.currentPlate;
    }
    renderSlotsGrid();
    updateRibbonCounts();
});

// Quick fill test plate
function fillPlate(plate) {
    document.getElementById('plateNumber').value = plate;
}

// Fetch live slots on page load
async function fetchSlots() {
    try {
        const res = await fetch('/api/slots');
        const data = await res.json();
        if (data.success) {
            allSlots = data.slots;
            renderSlotsGrid();
            updateRibbonCounts();
        }
    } catch (err) {
        console.error('Error fetching slots:', err);
    }
}

function updateRibbonCounts() {
    const free = allSlots.filter(s => s.status === 'FREE').length;
    const occupied = allSlots.filter(s => s.status === 'OCCUPIED').length;
    document.getElementById('freeSlotsCount').textContent = free;
    document.getElementById('occupiedSlotsCount').textContent = occupied;
    document.getElementById('totalSlotsCount').textContent = allSlots.length;
}

function renderSlotsGrid() {
    const container = document.getElementById('slotsGrid');
    if (!container) return;

    // Group slots by Zone
    const zones = {
        1: { name: 'Ground Floor — Zone A (Near Main Entrance)', slots: [] },
        2: { name: 'Ground Floor — Zone B (West Wing)', slots: [] },
        3: { name: 'Upper Floor — Zone C (Rooftop Deck via Ramp)', slots: [] }
    };

    allSlots.forEach(s => {
        if (zones[s.zoneId]) {
            zones[s.zoneId].slots.push(s);
        }
    });

    let html = '';

    for (const [zId, zData] of Object.entries(zones)) {
        if (activeZoneFilter !== 'all' && activeZoneFilter !== zId) {
            continue;
        }

        const freeInZone = zData.slots.filter(s => s.status === 'FREE').length;

        html += `
        <div class="zone-group">
            <div class="zone-title">
                <span><i class="fa-solid fa-layer-group"></i> ${zData.name}</span>
                <span class="badge ${freeInZone > 0 ? 'text-green' : 'text-danger'}">${freeInZone} Free / ${zData.slots.length}</span>
            </div>
            <div class="slots-grid-matrix">
        `;

        zData.slots.forEach(slot => {
            const isFree = (slot.status === 'FREE');
            const statusClass = isFree ? 'slot-free' : 'slot-occupied';
            const icon = isFree ? 'fa-square-parking' : 'fa-car-side';

            html += `
            <div class="parking-bay ${statusClass}" id="bay-${slot.slotId}" data-id="${slot.slotId}">
                <span class="bay-label">${slot.slotLabel}</span>
                <div class="bay-icon"><i class="fa-solid ${icon}"></i></div>
                <div class="bay-distance">${slot.distance.toFixed(1)}m</div>
                ${!isFree && slot.currentPlate ? `<div class="bay-plate">${slot.currentPlate}</div>` : ''}
            </div>
            `;
        });

        html += `
            </div>
        </div>
        `;
    }

    container.innerHTML = html;
}

// Zone filter tabs
document.addEventListener('DOMContentLoaded', () => {
    fetchSlots();

    // Zone tabs
    const tabs = document.querySelectorAll('.zone-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeZoneFilter = tab.dataset.zone;
            renderSlotsGrid();
        });
    });

    // Arrival Registration Form Submission (Module 1 & 2)
    const entryForm = document.getElementById('entryForm');
    if (entryForm) {
        entryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const plate = document.getElementById('plateNumber').value.trim().toUpperCase();
            const vType = document.getElementById('vehicleType').value;
            const btn = document.getElementById('btnAllocate');

            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Finding nearest slot...';

            try {
                const res = await fetch('/api/entry', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ plateNumber: plate, vehicleType: vType })
                });

                const data = await res.json();

                if (data.success) {
                    // Show allocation card
                    const allocCard = document.getElementById('allocationResultCard');
                    document.getElementById('allocatedSlotLabel').textContent = data.allocatedSlot.slotLabel;
                    document.getElementById('allocatedPlate').textContent = data.plateNumber;
                    document.getElementById('allocatedDistance').textContent = `${data.allocatedSlot.distance} meters`;
                    document.getElementById('allocatedZone').textContent = `Zone ${data.allocatedSlot.zoneId === 1 ? 'A' : (data.allocatedSlot.zoneId === 2 ? 'B' : 'C')}`;
                    document.getElementById('allocatedRow').textContent = data.allocatedSlot.row;
                    document.getElementById('allocatedCol').textContent = data.allocatedSlot.col;

                    allocCard.style.display = 'block';

                    // Highlight the target bay visually
                    setTimeout(() => {
                        const targetBay = document.getElementById(`bay-${data.allocatedSlot.slotId}`);
                        if (targetBay) {
                            targetBay.classList.add('slot-nearest-target');
                            targetBay.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);

                    // Reset form input
                    document.getElementById('plateNumber').value = '';
                } else {
                    alert(data.error || 'Failed to allocate slot');
                }
            } catch (err) {
                console.error('Entry error:', err);
                alert('Network or server error during entry registration');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-bullseye"></i> Register Arrival &amp; Get Nearest Slot';
                fetchSlots();
            }
        });
    }
});
