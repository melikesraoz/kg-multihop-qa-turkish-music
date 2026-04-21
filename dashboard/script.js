// Dashboard Logic - Final Stability Fix
const stats = (typeof projectData !== 'undefined') ? projectData : {
    overview: { entities: 0, relations: 0, paths: 0 },
    distribution: { labels: [], data: [] },
    seeds: [],
    relationFrequency: { labels: [], data: [] },
    relationImportance: { labels: [], data: [] },
    curves: [],
    traceLibrary: []
};

// UI: Section switching
function showSection(sectionId) {
    console.log("Navigating to:", sectionId);
    document.querySelectorAll('.dashboard-section').forEach(s => {
        s.classList.remove('active');
        s.style.display = 'none'; // Forced hide
    });
    document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
    
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        section.style.display = 'block'; // Forced show
        section.style.opacity = '1';
        section.style.visibility = 'visible';
    }
    
    document.querySelectorAll('.nav-links li').forEach(li => {
        if (li.getAttribute('onclick') && li.getAttribute('onclick').includes(sectionId)) {
            li.classList.add('active');
        }
    });

    // Handle Chart.js resize in hidden tabs
    setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
}

// Charts Global Manager
let charts = {};

function initCharts() {
    console.log("Initializing charts with v4 syntax...");
    
    const sharedScales = {
        y: { 
            grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false }, 
            ticks: { color: '#94a3b8', font: { size: 10 } } 
        },
        x: { 
            grid: { display: false }, 
            ticks: { color: '#94a3b8', font: { size: 10 } } 
        }
    };

    // 1. Distribution (Pie)
    const distCtx = document.getElementById('distChart');
    if (distCtx) {
        charts.dist = new Chart(distCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: stats.distribution.labels.length ? stats.distribution.labels : ['No Data'],
                datasets: [{
                    data: stats.distribution.data.length ? stats.distribution.data : [1],
                    backgroundColor: ['#00f3ff', '#bd00ff', '#00ff85', '#facc15', '#f87171', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', boxWidth: 12 } } } }
        });
    }

    // 2. Training Curves (Line)
    const curveCtx = document.getElementById('curveChart');
    if (curveCtx) {
        charts.curves = new Chart(curveCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: stats.curves.map(d => d.epoch),
                datasets: [
                    { label: 'Train Loss', data: stats.curves.map(d => d.train_loss), borderColor: '#f87171', tension: 0.3, pointRadius: 0 },
                    { label: 'Accuracy', data: stats.curves.map(d => d.accuracy), borderColor: '#00ff85', tension: 0.3, pointRadius: 0 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: sharedScales,
                plugins: { legend: { labels: { color: '#94a3b8' } } }
            }
        });
    }

    // 3. Top Relation Types (Horizontal Bar)
    const relCtx = document.getElementById('relBarChart');
    if (relCtx) {
        charts.rel = new Chart(relCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: stats.relationFrequency.labels,
                datasets: [{ 
                    label: 'Frequency', 
                    data: stats.relationFrequency.data, 
                    backgroundColor: '#00f3ff', 
                    borderRadius: 4, 
                    barThickness: 15 
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bars
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { display: false }, ticks: { color: '#94a3b8', autoSkip: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 4. Feature Importance (Horizontal Bar)
    const impCtx = document.getElementById('importanceChart');
    if (impCtx) {
        charts.imp = new Chart(impCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: stats.relationImportance.labels,
                datasets: [{ 
                    label: 'Importance', 
                    data: stats.relationImportance.data, 
                    backgroundColor: '#bd00ff', 
                    borderRadius: 4, 
                    barThickness: 15 
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { display: false }, ticks: { color: '#94a3b8', autoSkip: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 5. Domain Bar (Vertical)
    const domCtx = document.getElementById('domainBarChart');
    if (domCtx) {
        charts.dom = new Chart(domCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Football', 'Cinema', 'Business', 'Music', 'Academia'],
                datasets: [{ label: 'F1 %', data: [84.1, 81.2, 79.5, 84.7, 76.2], backgroundColor: '#00ff85', borderRadius: 4 }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: sharedScales }
        });
    }
}

// Data Population
function populateData() {
    console.log("Populating dashboard text blocks...");
    
    // Overview Stats
    if (stats.overview) {
        setSafeText('stat-ent', stats.overview.entities.toLocaleString());
        setSafeText('stat-rel', stats.overview.relations.toLocaleString());
        setSafeText('stat-paths', stats.overview.paths.toLocaleString());
    }

    // Seed Entities Table
    const seedBody = document.getElementById('seed-body');
    if (seedBody && stats.seeds) {
        seedBody.innerHTML = '';
        stats.seeds.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td><span class="badge wikidata">${s.type}</span></td>
                <td style="font-family: JetBrains Mono; color: #00f3ff;">${s.relations}</td>
            `;
            seedBody.appendChild(tr);
        });
    }

    // XAI Evidence Case Study
    if (stats.traceLibrary && stats.traceLibrary.length > 0) {
        const tr = stats.traceLibrary[0];
        setSafeText('xai-question', tr.question);
        setSafeText('xai-answer', tr.summary || tr.ans);
        
        const pathDiv = document.getElementById('xai-path');
        if (pathDiv) {
            pathDiv.innerHTML = `
                <div class="path-node">Z\u00fclf\u00fc Livaneli</div>
                <div class="path-edge">\u2193 place of birth</div>
                <div class="path-node">Ilg\u0131n</div>
                <div class="path-edge">\u2193 located in adm. entity</div>
                <div class="path-node">Konya Province</div>
            `;
        }

        const traceDiv = document.getElementById('xai-trace');
        if (traceDiv) {
            traceDiv.innerHTML = '';
            tr.hops.forEach(h => {
                const step = document.createElement('div');
                step.className = 'trace-step';
                step.innerHTML = `
                    <div class="step-num">${h.num}</div>
                    <div class="step-content">
                        <h4>${h.title}</h4>
                        <p>${h.desc}</p>
                    </div>
                `;
                traceDiv.appendChild(step);
            });
        }
    }

    // Comparison Table
    const compBody = document.querySelector('#comp-table tbody');
    if (compBody) {
        compBody.innerHTML = '';
        const methods = [
            ['No-Retrieval', 34.0, 0.411, 0.340, '-'],
            ['Vanilla RAG', 34.0, 0.399, 0.340, '0.602'],
            ['Vanilla QE', 28.0, 0.329, 0.280, '0.641'],
            ['KG-Infused RAG', 60.0, 0.681, 0.600, '0.824']
        ];
        methods.forEach(m => {
            const tr = document.createElement('tr');
            if (m[0].includes('KG-')) tr.style.background = 'rgba(0,243,255,0.05)';
            tr.innerHTML = `<td>${m[0]}</td><td>${m[1]}%</td><td>${m[2]}</td><td>${m[3]}</td><td>${m[4]}</td>`;
            compBody.appendChild(tr);
        });
    }
}

function setSafeText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

window.addEventListener('load', () => {
    populateData();
    initCharts();
});
