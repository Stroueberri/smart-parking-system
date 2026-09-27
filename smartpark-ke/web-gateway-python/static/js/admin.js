/**
 * SmartPark KE — Admin Analytics & Management Dashboard
 * Module 9: Admin & Reporting Module, Module 7 FSM Audit, Dynamic Tariffs
 */

let revenueChartInstance = null;
let occupancyChartInstance = null;

async function loadDashboardData() {
    await Promise.all([
        loadRevenueAnalytics(),
        loadOccupancyAnalytics(),
        loadOverstayAlerts(),
        loadBarrierFsmHistory(),
        loadTariffTable()
    ]);
}

// 1. Revenue Analytics (Module 9)
async function loadRevenueAnalytics() {
    try {
        const res = await fetch('/api/reports/revenue');
        const data = await res.json();

        document.getElementById('totalRevenue').textContent = `Kshs ${data.totalRevenue.toFixed(2)}`;
        document.getElementById('completedSessions').textContent = data.completedSessions;
        document.getElementById('activeVehicles').textContent = data.activeSessions;

        // Render Chart.js Revenue Chart
        const ctx = document.getElementById('revenueChart').getContext('2d');
        const transactions = data.recentTransactions || [];

        const labels = transactions.length > 0
            ? transactions.map(t => `${t.plate}`)
            : ['Sample 1', 'Sample 2', 'Sample 3'];
        const values = transactions.length > 0
            ? transactions.map(t => t.amount)
            : [50, 100, 300];

        if (revenueChartInstance) {
            revenueChartInstance.destroy();
        }

        revenueChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Amount Collected (Kshs)',
                    data: values,
                    backgroundColor: 'rgba(37, 99, 235, 0.75)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
    } catch (err) {
        console.error('Revenue analytics error:', err);
    }
}

// 2. Occupancy Analytics
async function loadOccupancyAnalytics() {
    try {
        const res = await fetch('/api/reports/occupancy');
        const data = await res.json();

        document.getElementById('occupancyRate').textContent = `${data.occupancyRate}%`;
        document.getElementById('occupancySub').textContent = `${data.occupiedSlots} / ${data.totalSlots} slots occupied`;

        // Render Zone breakdown chart
        const ctx = document.getElementById('occupancyChart').getContext('2d');
        const zones = data.zoneBreakdown || [];

        const labels = zones.map(z => z.name.split('(')[0].trim());
        const occupied = zones.map(z => z.occupied);
        const free = zones.map(z => z.free);

        if (occupancyChartInstance) {
            occupancyChartInstance.destroy();
        }

        occupancyChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: zones.length > 0 ? labels : ['Zone A', 'Zone B', 'Zone C'],
                datasets: [{
                    data: zones.length > 0 ? occupied : [2, 1, 0],
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
                    borderWidth: 2,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                }
            }
        });
    } catch (err) {
        console.error('Occupancy analytics error:', err);
    }
}

// 3. Overstay Alerts (Module 4 & 9)
async function loadOverstayAlerts() {
    try {
        const res = await fetch('/api/reports/overstay?threshold=360');
        const data = await res.json();

        const badge = document.getElementById('overstayBadge');
        const tbody = document.getElementById('overstayTableBody');

        badge.textContent = `${data.overstayVehicles.length} Overstaying`;

        if (data.overstayVehicles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No vehicles currently overstaying (&gt; 6 hours).</td></tr>';
            return;
        }

        let html = '';
        data.overstayVehicles.forEach(v => {
            html += `
            <tr>
                <td><strong>${v.plateNumber}</strong></td>
                <td><span class="badge">${v.slotLabel}</span></td>
                <td>${v.entryTime}</td>
                <td><span class="text-danger font-bold">${v.durationMinutes} mins</span></td>
                <td><button class="btn btn-sm btn-outline" onclick="alert('Notice issued for ' + '${v.plateNumber}')">Issue Notice</button></td>
            </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        console.error('Overstay alerts error:', err);
    }
}

// 4. Barrier FSM History (LIFO Stack - Module 7)
async function loadBarrierFsmHistory() {
    try {
        const res = await fetch('/api/barrier/status');
        const data = await res.json();

        const stateBadge = document.getElementById('fsmCurrentState');
        stateBadge.textContent = data.currentState;
        stateBadge.className = data.currentState === 'OPEN' ? 'badge badge-success' : 'badge badge-primary';

        const historyBox = document.getElementById('barrierStackHistory');
        const history = data.history || [];

        if (history.length === 0) {
            historyBox.innerHTML = '<p class="text-muted text-center">No barrier transitions recorded yet.</p>';
            return;
        }

        let html = '';
        history.forEach((h, idx) => {
            const isTop = (idx === 0);
            html += `
            <div class="stack-item ${isTop ? 'top' : ''}">
                <div>
                    <strong>#${h.id} ${h.from} &rarr; ${h.to}</strong>
                    <div class="text-muted" style="font-size:0.75rem;">Trigger: ${h.trigger}</div>
                </div>
                <div class="text-muted" style="font-size:0.75rem;">
                    ${h.time} ${isTop ? '<span class="badge badge-success" style="font-size:0.65rem;">STACK TOP</span>' : ''}
                </div>
            </div>
            `;
        });
        historyBox.innerHTML = html;
    } catch (err) {
        console.error('Barrier FSM history error:', err);
    }
}

// 5. Dynamic Tariff Table (Section 5)
async function loadTariffTable() {
    try {
        const res = await fetch('/api/tariffs');
        const data = await res.json();

        const tbody = document.getElementById('tariffTableBody');
        let html = '';

        data.tariffs.forEach(t => {
            const maxLabel = t.maxMinutes >= 1440 ? 'Full Day / > 6h' : `Up to ${t.maxMinutes} mins`;
            html += `
            <tr>
                <td>#${t.tariffId}</td>
                <td><strong>${maxLabel}</strong></td>
                <td>Kshs ${t.fee.toFixed(2)}</td>
                <td>${t.description}</td>
            </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        console.error('Tariff load error:', err);
    }
}

// Modal controls for adding tariff
function showAddTariffModal() {
    document.getElementById('tariffModal').style.display = 'flex';
}

function closeTariffModal() {
    document.getElementById('tariffModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();

    const addTariffForm = document.getElementById('addTariffForm');
    if (addTariffForm) {
        addTariffForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const mins = document.getElementById('newMaxMinutes').value;
            const fee = document.getElementById('newFee').value;
            const desc = document.getElementById('newDescription').value;

            try {
                const res = await fetch('/api/tariffs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ maxMinutes: mins, fee: fee, description: desc })
                });
                const data = await res.json();
                if (data.success) {
                    closeTariffModal();
                    loadTariffTable();
                } else {
                    alert('Failed to save tariff');
                }
            } catch (err) {
                console.error('Error adding tariff:', err);
            }
        });
    }
});
