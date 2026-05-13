let autoRunInterval = null;
let currentFile = null;

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) throw new Error("Server error");
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error("Error fetching status:", error);
    }
}

function updateUI(data) {
    // 1. Status Bar & Settings
    document.getElementById('scheduler-mode-display').innerText = `Mode: ${data.scheduler_settings.type}`;
    document.getElementById('quantum-display').innerText = data.scheduler_settings.quantum;

    // 2. CPU Panel - The "Heart" of the Dashboard
    const running = data.cpu.running_process;
    const cpuBadge = document.getElementById('cpu-status-badge');
    const cpuName = document.getElementById('cpu-proc-name');
    const cpuPid = document.getElementById('cpu-proc-id');
    const cpuBurst = document.getElementById('cpu-proc-burst');
    const cpuPercentText = document.getElementById('cpu-percent');
    const cpuBar = document.getElementById('cpu-progress-bar');
    const cpuSlice = document.getElementById('cpu-slice');
    const cpuAlgoType = document.getElementById('cpu-algo-type');
    const cpuPrioWrapper = document.getElementById('cpu-proc-prio-wrapper');
    const cpuPrio = document.getElementById('cpu-proc-prio');

    cpuAlgoType.innerText = data.scheduler_settings.type;

    if (running) {
        cpuBadge.innerText = "CPU EXECUTING";
        cpuBadge.className = "badge bg-primary shadow-sm";
        cpuName.innerText = running.name;
        cpuPid.innerText = `PROCESS ID: ${running.pid}`;
        cpuBurst.innerText = running.remaining_burst_time;
        
        // Find current turn slice
        const lastGantt = data.cpu.gantt_chart[data.cpu.gantt_chart.length - 1];
        const sliceTime = lastGantt ? (lastGantt.end - lastGantt.start) : 0;
        cpuSlice.innerText = `${sliceTime} CPU Units`;

        if (data.scheduler_settings.type === 'Priority') {
            cpuPrioWrapper.classList.remove('d-none');
            cpuPrio.innerText = running.priority;
        } else {
            cpuPrioWrapper.classList.add('d-none');
        }
        
        const percent = Math.round(((running.burst_time - running.remaining_burst_time) / running.burst_time) * 100);
        cpuPercentText.innerText = `${percent}%`;
        cpuBar.style.width = `${percent}%`;
        
        animateFlow('node-cpu');
    } else {
        cpuBadge.innerText = "CPU IDLE";
        cpuBadge.className = "badge bg-success shadow-sm";
        cpuName.innerText = "IDLE";
        cpuPid.innerText = "NO ACTIVE PROCESS";
        cpuBurst.innerText = "0";
        cpuSlice.innerText = "0 Units";
        cpuPercentText.innerText = "0%";
        cpuBar.style.width = "0%";
        cpuPrioWrapper.classList.add('d-none');
        resetFlow();
    }

    // 3. Memory Visualizer & Stats
    document.getElementById('stat-frag').innerText = `${data.memory.frag_percent}%`;
    document.getElementById('stat-holes').innerText = data.memory.free_holes;
    document.getElementById('stat-used').innerText = data.memory.used;
    document.getElementById('stat-large').innerText = data.memory.largest_free;

    const memMap = document.getElementById('memory-map-container');
    memMap.innerHTML = '';
    data.memory.blocks.forEach(block => {
        const div = document.createElement('div');
        div.className = `mem-block ${block.free ? 'mem-free' : 'mem-alloc'}`;
        div.style.width = `calc(${(block.size / data.memory.total) * 100}% - 4px)`;
        div.title = `${block.free ? 'Free' : 'P' + block.pid}: ${block.size}KB`;
        if (!block.free) div.innerText = `P${block.pid}`;
        memMap.appendChild(div);
    });

    // 4. Tables: PCB & Inodes
    const tablePcb = document.getElementById('table-pcb');
    tablePcb.innerHTML = '';
    data.processes.forEach(p => {
        tablePcb.innerHTML += `
            <tr>
                <td class="ps-3 text-secondary">#${p.pid}</td>
                <td class="fw-bold">${p.name}</td>
                <td><span class="badge bg-dark border border-secondary text-secondary">${p.priority}</span></td>
                <td>${p.remaining_burst_time}</td>
                <td class="pe-3"><span class="badge ${getStateClass(p.state)}">${p.state}</span></td>
            </tr>`;
    });

    const inodeTable = document.getElementById('table-inodes');
    inodeTable.innerHTML = '';
    data.files.forEach(f => {
        const blocksHtml = f.data_blocks.map(b => `<span class="inode-block-visual">[${b}]</span>`).join('');
        inodeTable.innerHTML += `<tr><td class="ps-2">#${f.inode_number}</td><td>${f.filename}</td><td>${blocksHtml}</td><td class="pe-2 text-info fw-bold">${f.file_size}B</td></tr>`;
    });

    // 5. Queues
    const readyContainer = document.getElementById('container-ready');
    readyContainer.innerHTML = '';
    data.cpu.ready_queue.forEach(p => {
        readyContainer.innerHTML += `<div class="badge bg-success border border-success border-opacity-25 px-3 py-2 shadow-sm">${p.name}</div>`;
    });
    if (data.cpu.ready_queue.length > 0) animateFlow('node-queue');

    const waitingContainer = document.getElementById('container-waiting');
    const waitingEmpty = document.getElementById('waiting-empty-msg');
    waitingContainer.innerHTML = '';
    
    if (data.cpu.waiting_queue.length > 0) {
        waitingEmpty.classList.add('d-none');
        data.cpu.waiting_queue.forEach(p => {
            const item = document.createElement('div');
            item.className = 'list-group-item waiting-item border-0';
            const totalWait = 5; // Fixed for progress visualization
            const progress = ((totalWait - p.wait_time) / totalWait) * 100;
            
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold text-white"><i class="fas fa-cog wait-spinner me-2"></i>${p.name}</span>
                    <span class="extra-small text-warning fw-bold">${p.wait_time} ticks left</span>
                </div>
                <div class="extra-small text-secondary mb-1">Reason: <span class="text-info">${p.wait_reason}</span></div>
                <div class="progress wait-progress">
                    <div class="progress-bar bg-warning" style="width: ${progress}%"></div>
                </div>
            `;
            waitingContainer.appendChild(item);
        });
    } else {
        waitingEmpty.classList.remove('d-none');
    }

    // 6. Gantt Chart - New Professional Rendering
    const gantt = document.getElementById('gantt-chart-container');
    gantt.innerHTML = '';
    
    data.cpu.gantt_chart.forEach((entry, idx) => {
        const block = document.createElement('div');
        block.className = 'gantt-block bg-primary';
        
        const duration = entry.end - entry.start;
        const width = Math.max(40, duration * 40);
        block.style.width = `${width}px`;
        
        block.title = `${entry.name}\nStart: ${entry.start}\nEnd: ${entry.end}\nDuration: ${duration}`;
        block.innerHTML = `<span class="gantt-label">${entry.name}</span>`;
        
        // Start Time Marker (ONLY for the very first block)
        if (idx === 0) {
            const startMarker = document.createElement('span');
            startMarker.className = 'gantt-time-marker';
            startMarker.innerText = entry.start;
            block.appendChild(startMarker);
        }
        
        // End Time Marker (for every block to show boundaries)
        const endMarker = document.createElement('span');
        endMarker.className = 'gantt-time-marker end-marker';
        endMarker.innerText = entry.end;
        block.appendChild(endMarker);
        
        gantt.appendChild(block);
    });

    // 7. File Explorer
    const fileContainer = document.getElementById('container-files');
    fileContainer.innerHTML = '';
    data.files.forEach(f => {
        const item = document.createElement('div');
        item.className = 'file-item d-flex justify-content-between align-items-center px-3 py-2 border-bottom border-secondary border-opacity-25';
        item.onclick = () => openFile(f);
        item.innerHTML = `
            <div>
                <div class="small fw-bold text-info"><i class="far fa-file-alt me-2"></i>${f.filename}</div>
                <div class="extra-small text-white opacity-75 fw-bold">Size: ${f.file_size} Bytes | Created: ${f.created_at}</div>
            </div>
            <div class="file-actions">
                <i class="fas fa-eye text-secondary me-2 small"></i>
            </div>
        `;
        fileContainer.appendChild(item);
    });

    // 8. Logs with Color Coding & Auto-Scroll
    const logList = document.getElementById('log-list');
    const wasAtBottom = logList.scrollHeight - logList.scrollTop <= logList.clientHeight + 1;
    
    logList.innerHTML = '';
    data.logs.forEach(log => {
        logList.innerHTML += `
            <div class="log-entry log-${log.category}">
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-msg">${log.message}</span>
            </div>`;
    });
    
    if (wasAtBottom) logList.scrollTop = logList.scrollHeight;
}

function getStateClass(state) {
    switch (state) {
        case 'NEW': return 'state-new';
        case 'READY': return 'state-ready';
        case 'RUNNING': return 'state-running';
        case 'WAITING': return 'state-waiting';
        case 'TERMINATED': return 'state-terminated';
        default: return 'bg-secondary';
    }
}

function animateFlow(activeId) {
    resetFlow();
    document.getElementById(activeId).classList.add('active');
    if (activeId === 'node-cpu') {
        document.getElementById('node-pm').classList.add('active');
        document.getElementById('node-mm').classList.add('active');
        document.getElementById('node-queue').classList.add('active');
    }
}

function resetFlow() {
    document.querySelectorAll('.flow-node').forEach(n => n.classList.remove('active'));
}

// Global Actions
document.getElementById('btn-step').onclick = async () => {
    await fetch('/api/step', { method: 'POST' });
    fetchStatus();
};

document.getElementById('btn-reset').onclick = async () => {
    await fetch('/api/reset', { method: 'POST' });
    fetchStatus();
};

document.getElementById('btn-run').onclick = () => {
    const btn = document.getElementById('btn-run');
    if (autoRunInterval) {
        clearInterval(autoRunInterval);
        autoRunInterval = null;
        btn.innerHTML = '<i class="fas fa-forward me-1"></i> Auto-Run';
        btn.classList.replace('btn-danger', 'btn-primary');
    } else {
        autoRunInterval = setInterval(async () => {
            const res = await fetch('/api/status');
            const data = await res.json();
            if (data.processes.length > 0 && !data.cpu.running_process && data.cpu.ready_queue.length === 0 && data.cpu.waiting_queue.length === 0) {
                // Check if all are terminated
                const allTerminated = data.processes.every(p => p.state === 'TERMINATED');
                if (allTerminated) {
                    document.getElementById('btn-run').click();
                    return;
                }
            }
            await fetch('/api/step', { method: 'POST' });
            fetchStatus();
        }, 1000);
        btn.innerHTML = '<i class="fas fa-pause me-1"></i> Stop';
        btn.classList.replace('btn-primary', 'btn-danger');
    }
};

document.getElementById('select-algo').onchange = (e) => {
    const val = e.target.value;
    const desc = document.getElementById('algo-description');
    const note = document.getElementById('priority-note');
    if (val === 'Priority') {
        desc.innerHTML = '<i class="fas fa-info-circle me-1"></i> Prio: CPU selects the highest priority first, executing for one quantum per turn.';
        note.classList.remove('d-none');
    } else {
        desc.innerHTML = '<i class="fas fa-info-circle me-1"></i> RR: Standard Round Robin execution using fixed time slices (Quantum).';
        note.classList.add('d-none');
    }
};

document.getElementById('btn-apply-settings').onclick = async () => {
    const data = {
        type: document.getElementById('select-algo').value === 'RR' ? 'Round Robin' : 'Priority',
        quantum: document.getElementById('input-quantum').value
    };
    await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    fetchStatus();
};

document.getElementById('btn-create-p').onclick = async () => {
    const data = {
        name: document.getElementById('p-name').value,
        burst: document.getElementById('p-burst').value,
        memory: document.getElementById('p-mem').value,
        priority: document.getElementById('p-prio').value
    };
    const res = await fetch('/api/process/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (res.ok) {
        bootstrap.Modal.getInstance(document.getElementById('modal-proc')).hide();
        fetchStatus();
    }
};

document.getElementById('btn-create-f').onclick = async () => {
    const data = {
        name: document.getElementById('f-name').value,
        content: document.getElementById('f-content').value
    };
    await fetch('/api/file/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    bootstrap.Modal.getInstance(document.getElementById('modal-file')).hide();
    fetchStatus();
};

// Demo Scenarios
window.loadDemo = async (type) => {
    await fetch('/api/reset', { method: 'POST' });
    
    if (type === 'RR') {
        await createP("Task_A", 1, 6, 150);
        await createP("Task_B", 1, 4, 100);
        await setSettings("Round Robin", 2);
    } else if (type === 'PRIO') {
        await createP("Low_Prio", 1, 8, 100);
        await createP("High_Prio", 10, 5, 200);
        await setSettings("Priority", 2);
    } else if (type === 'IO') {
        await createP("I/O_Heavy", 1, 10, 100);
        await setSettings("Round Robin", 2);
    } else if (type === 'FRAG') {
        await createP("P1", 1, 10, 400);
        await createP("P2", 1, 10, 200);
        await createP("P3", 1, 10, 300);
    }
    
    fetchStatus();
};

async function createP(name, prio, burst, mem) {
    return fetch('/api/process/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, priority: prio, burst, memory: mem })
    });
}

async function setSettings(type, quantum) {
    return fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, quantum })
    });
}

// File Interactions
window.openFile = (file) => {
    currentFile = file.filename;
    const modal = new bootstrap.Modal(document.getElementById('modal-file-view'));
    
    // Set Metadata
    const blocksHtml = file.data_blocks.map(b => `[${b}]`).join(' ');
    document.getElementById('file-metadata').innerHTML = `
        <i class="fas fa-info-circle me-1"></i> Size: ${file.file_size} Bytes | Blocks: ${blocksHtml}
    `;
    
    // View Mode Content
    document.getElementById('view-file-title').innerText = `VIEWING: ${file.filename}`;
    document.getElementById('file-view-mode').innerText = file.content;
    document.getElementById('view-file-content').value = file.content;
    
    // UI Reset
    document.getElementById('file-view-mode').classList.remove('d-none');
    document.getElementById('view-file-content').classList.add('d-none');
    document.getElementById('btn-edit-mode').classList.remove('d-none');
    document.getElementById('btn-save-file').classList.add('d-none');
    
    modal.show();
};

document.getElementById('btn-edit-mode').onclick = () => {
    document.getElementById('view-file-title').innerText = `EDITING: ${currentFile}`;
    document.getElementById('file-view-mode').classList.add('d-none');
    document.getElementById('view-file-content').classList.remove('d-none');
    document.getElementById('btn-edit-mode').classList.add('d-none');
    document.getElementById('btn-save-file').classList.remove('d-none');
};

document.getElementById('btn-save-file').onclick = async () => {
    const content = document.getElementById('view-file-content').value;
    await fetch('/api/file/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: currentFile, content: content })
    });
    bootstrap.Modal.getInstance(document.getElementById('modal-file-view')).hide();
    fetchStatus();
};

document.getElementById('btn-delete-file-modal').onclick = async () => {
    if (confirm(`ARE YOU SURE YOU WANT TO DELETE ${currentFile}?`)) {
        await fetch('/api/file/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: currentFile })
        });
        bootstrap.Modal.getInstance(document.getElementById('modal-file-view')).hide();
        fetchStatus();
    }
};

window.deleteFile = async (name) => {
    if (confirm(`ARE YOU SURE YOU WANT TO DELETE ${name}?`)) {
        await fetch('/api/file/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        });
        fetchStatus();
    }
};

// Init Tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Start
fetchStatus();
setInterval(fetchStatus, 5000);
