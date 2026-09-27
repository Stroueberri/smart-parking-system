/**
 * SmartPark KE — Attendant / Exit Kiosk JavaScript
 * Modules 5, 6, 7 & 11: Fee Calculation, M-Pesa STK Push, Barrier Actuator & SMS Receipt
 */

let currentCheckoutRequestId = null;
let currentSessionId = null;
let currentBillData = null;

const socket = io();

socket.on('connect', () => {
    console.log('[Socket.IO] Attendant kiosk connected to live gateway');
});

// Real-time Barrier State Change Listener (Module 7)
socket.on('barrier_state_changed', (event) => {
    console.log('[WebSocket] Barrier state change:', event);
    updateBarrierUi(event.state);
});

function updateBarrierUi(state) {
    const arm = document.getElementById('barrierArm');
    const lightRed = document.getElementById('lightRed');
    const lightGreen = document.getElementById('lightGreen');
    const statePill = document.getElementById('barrierCurrentState');

    if (statePill) statePill.textContent = state;

    if (state === 'OPEN' || state === 'OPENING') {
        if (arm) arm.classList.add('raised');
        if (lightRed) lightRed.classList.remove('active');
        if (lightGreen) lightGreen.classList.add('active');
    } else {
        if (arm) arm.classList.remove('raised');
        if (lightGreen) lightGreen.classList.remove('active');
        if (lightRed) lightRed.classList.add('active');
    }
}

// Fetch active slots on load to show quick-test plates
async function loadActivePlates() {
    try {
        const res = await fetch('/api/slots');
        const data = await res.json();
        const activeContainer = document.getElementById('activePlatesList');
        if (activeContainer && data.slots) {
            const occupied = data.slots.filter(s => s.status === 'OCCUPIED' && s.currentPlate);
            if (occupied.length > 0) {
                let html = '<span class="quick-label">Active Inside:</span>';
                occupied.forEach(s => {
                    html += `<button type="button" class="btn-chip" onclick="searchPlate('${s.currentPlate}')">${s.currentPlate} (${s.slotLabel})</button> `;
                });
                activeContainer.innerHTML = html;
            } else {
                activeContainer.innerHTML = '<span class="quick-label">No vehicles currently inside. Register one on Driver Display to test.</span>';
            }
        }
    } catch (err) {
        console.error('Error fetching active plates:', err);
    }
}

function searchPlate(plate) {
    document.getElementById('lookupPlate').value = plate;
    document.getElementById('lookupForm').dispatchEvent(new Event('submit'));
}

document.addEventListener('DOMContentLoaded', () => {
    loadActivePlates();

    // 1. Vehicle Exit Lookup (Module 5)
    const lookupForm = document.getElementById('lookupForm');
    if (lookupForm) {
        lookupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const plate = document.getElementById('lookupPlate').value.trim().toUpperCase();
            const btn = document.getElementById('btnSearch');

            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Finding...';

            try {
                const res = await fetch(`/api/exit/${encodeURIComponent(plate)}`);
                const data = await res.json();

                if (data.success) {
                    currentBillData = data;
                    currentSessionId = data.sessionId;

                    document.getElementById('billPlate').textContent = data.plateNumber;
                    document.getElementById('billSlot').textContent = data.slotLabel;
                    document.getElementById('billEntryTime').textContent = data.entryTime;
                    document.getElementById('billExitTime').textContent = data.exitTime;
                    document.getElementById('billDuration').textContent = `${data.formattedDuration} (${data.durationMinutes} mins)`;
                    document.getElementById('billTariffDesc').textContent = data.tariffApplied;
                    document.getElementById('billAmount').textContent = `Kshs ${data.fee.toFixed(2)}`;
                    document.getElementById('stkSessionId').value = data.sessionId;

                    const statusBadge = document.getElementById('paymentStatusBadge');
                    const stkSec = document.getElementById('stkSection');
                    const paidBox = document.getElementById('paidConfirmationBox');

                    if (data.paid) {
                        statusBadge.textContent = 'PAID';
                        statusBadge.className = 'badge badge-success';
                        stkSec.style.display = 'none';
                        paidBox.style.display = 'block';
                    } else {
                        statusBadge.textContent = 'UNPAID';
                        statusBadge.className = 'badge badge-unpaid';
                        stkSec.style.display = 'block';
                        paidBox.style.display = 'none';
                        document.getElementById('stkStatusBox').style.display = 'none';
                    }

                    document.getElementById('billCard').style.display = 'block';
                } else {
                    alert(data.error || 'Vehicle session not found');
                }
            } catch (err) {
                console.error('Lookup error:', err);
                alert('Error looking up session bill');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-search"></i> Find Bill';
            }
        });
    }

    // 2. M-Pesa STK Push Initiation (Module 6)
    const stkForm = document.getElementById('stkForm');
    if (stkForm) {
        stkForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const phone = document.getElementById('phoneNumber').value.trim();
            const btn = document.getElementById('btnStkPush');

            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Dispatching STK Push...';

            try {
                const res = await fetch('/api/payment/stk-push', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sessionId: currentSessionId,
                        phoneNumber: phone
                    })
                });

                const data = await res.json();

                if (data.success) {
                    currentCheckoutRequestId = data.checkoutRequestId;
                    const statusBox = document.getElementById('stkStatusBox');
                    document.getElementById('stkCheckoutId').textContent = data.checkoutRequestId;
                    document.getElementById('stkStatusText').textContent = data.message;
                    statusBox.style.display = 'block';
                } else {
                    alert(data.error || 'Failed to trigger STK push');
                }
            } catch (err) {
                console.error('STK Push error:', err);
                alert('Error initiating M-Pesa payment');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send M-Pesa STK Push';
            }
        });
    }

    // 3. Simulate Customer Enters PIN (Sandbox Callback - Module 6 -> Module 7 & 11)
    const btnSimulatePin = document.getElementById('btnSimulatePin');
    if (btnSimulatePin) {
        btnSimulatePin.addEventListener('click', async () => {
            btnSimulatePin.disabled = true;
            btnSimulatePin.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Confirming PIN with Daraja...';

            try {
                const receiptNum = 'QKE' + Math.floor(10000000 + Math.random() * 90000000);
                const res = await fetch('/api/payment/confirm-webhook', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sessionId: currentSessionId,
                        mpesaReceipt: receiptNum,
                        amount: currentBillData ? currentBillData.fee : 50.0
                    })
                });

                const data = await res.json();

                if (data.success) {
                    // Update UI to paid state
                    document.getElementById('stkStatusBox').style.display = 'none';
                    document.getElementById('stkSection').style.display = 'none';
                    document.getElementById('paymentStatusBadge').textContent = 'PAID';
                    document.getElementById('paymentStatusBadge').className = 'badge badge-success';
                    document.getElementById('receiptNumber').textContent = data.mpesaReceipt;
                    document.getElementById('paidConfirmationBox').style.display = 'block';

                    // Update barrier actuator visualization
                    updateBarrierUi('OPEN');

                    // Show Module 11 SMS receipt preview
                    const smsBubble = document.getElementById('smsBubble');
                    smsBubble.innerHTML = `<strong>SAFARICOM M-PESA RECEIPT:</strong><br>
                    Confirmed. Kshs ${currentBillData ? currentBillData.fee.toFixed(2) : '50.00'} paid to SmartPark KE for vehicle ${currentBillData ? currentBillData.plateNumber : ''}.<br>
                    Receipt No: <strong>${data.mpesaReceipt}</strong>.<br>
                    Exit Gate 1 Opened. Safe travels!`;

                    loadActivePlates();
                } else {
                    alert(data.error || 'Payment confirmation failed');
                }
            } catch (err) {
                console.error('Payment confirmation error:', err);
                alert('Error confirming payment callback');
            } finally {
                btnSimulatePin.disabled = false;
                btnSimulatePin.innerHTML = '<i class="fa-solid fa-key"></i> Simulate Customer Enters M-Pesa PIN (Confirm Payment)';
            }
        });
    }

    // 4. Vehicle Passed (Sensor Cleared - Module 7)
    const btnVehiclePassed = document.getElementById('btnVehiclePassed');
    if (btnVehiclePassed) {
        btnVehiclePassed.addEventListener('click', async () => {
            try {
                await fetch('/api/barrier/sensor-cleared', { method: 'POST' });
                updateBarrierUi('CLOSED');
            } catch (err) {
                console.error('Barrier sensor error:', err);
            }
        });
    }

    // 5. Force Close Gate
    const btnForceClose = document.getElementById('btnForceClose');
    if (btnForceClose) {
        btnForceClose.addEventListener('click', async () => {
            try {
                await fetch('/api/barrier/sensor-cleared', { method: 'POST' });
                updateBarrierUi('CLOSED');
            } catch (err) {
                console.error('Force close error:', err);
            }
        });
    }
});
