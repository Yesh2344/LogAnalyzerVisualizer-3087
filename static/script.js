/**
 * Front‑end logic for fetching logs, rendering the table,
 * and drawing Chart.js visualizations.
 */

const logBody = document.getElementById('logBody');
const applyBtn = document.getElementById('applyFilters');

let hourChart = null;
let statusChart = null;

/**
 * Build the API query string from UI controls.
 */
function buildQuery() {
    const params = new URLSearchParams();
    const start = document.getElementById('start').value;
    const end = document.getElementById('end').value;
    const status = document.getElementById('status').value;

    if (start) params.append('start', new Date(start).toISOString());
    if (end) params.append('end', new Date(end).toISOString());
    if (status) params.append('status', status);

    return params.toString() ? `?${params}` : '';
}

/**
 * Fetch logs from the backend.
 */
async function fetchLogs() {
    const query = buildQuery();
    try {
        const response = await fetch(`/api/logs${query}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Failed to fetch logs');
        }
        const data = await response.json();
        renderTable(data);
        renderCharts(data);
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
}

/**
 * Populate HTML table with log entries.
 */
function renderTable(logs) {
    logBody.innerHTML = '';
    const fragment = document.createDocumentFragment();

    logs.forEach(entry => {
        const tr = document.createElement('tr');

        const tdTime = document.createElement('td');
        tdTime.textContent = new Date(entry.timestamp).toLocaleString();
        tr.appendChild(tdTime);

        const tdHost = document.createElement('td');
        tdHost.textContent = entry.host;
        tr.appendChild(tdHost);

        const tdMethod = document.createElement('td');
        tdMethod.textContent = entry.method;
        tr.appendChild(tdMethod);

        const tdPath = document.createElement('td');
        tdPath.textContent = entry.path;
        tr.appendChild(tdPath);

        const tdStatus = document.createElement('td');
        tdStatus.textContent = entry.status;
        tr.appendChild(tdStatus);

        const tdSize = document.createElement('td');
        tdSize.textContent = entry.size;
        tr.appendChild(tdSize);

        fragment.appendChild(tr);
    });

    logBody.appendChild(fragment);
}

/**
 * Prepare data and render Chart.js visualizations.
 */
function renderCharts(logs) {
    // Group by hour
    const hourCounts = {};
    logs.forEach(l => {
        const hour = new Date(l.timestamp).toISOString().substring(0, 13) + ':00';
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });
    const hourLabels = Object.keys(hourCounts).sort();
    const hourData = hourLabels.map(k => hourCounts[k]);

    // Group by status
    const statusCounts = {};
    logs.forEach(l => {
        const s = l.status;
        statusCounts[s] = (statusCounts[s] || 0) + 1;
    });
    const statusLabels = Object.keys(statusCounts);
    const statusData = statusLabels.map(k => statusCounts[k]);

    // Destroy previous charts if they exist
    if (hourChart) hourChart.destroy();
    if (statusChart) statusChart.destroy();

    const ctxHour = document.getElementById('hourChart').getContext('2d');
    hourChart = new Chart(ctxHour, {
        type: 'line',
        data: {
            labels: hourLabels,
            datasets: [{
                label: 'Requests per hour',
                data: hourData,
                borderColor: '#007bff',
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { display: true, title: { display: true, text: 'Hour' } },
                y: { display: true, title: { display: true, text: 'Requests' }, beginAtZero: true }
            }
        }
    });

    const ctxStatus = document.getElementById('statusChart').getContext('2d');
    statusChart = new Chart(ctxStatus, {
        type: 'pie',
        data: {
            labels: statusLabels,
            datasets: [{
                label: 'Status distribution',
                data: statusData,
                backgroundColor: [
                    '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Initial load
fetchLogs();

// Bind filter button
applyBtn.addEventListener('click', fetchLogs);