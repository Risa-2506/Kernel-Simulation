# Mini OS Kernel Simulator (Python)

A professional, modular Operating System kernel simulation with a modern dashboard-style terminal UI built using Python and the `rich` library.

## Features
- **Process Manager**: PCB management, state transitions (NEW, READY, RUNNING, TERMINATED).
- **CPU Scheduler**: Round Robin scheduling with configurable time quantum and Gantt chart generation.
- **Memory Manager**: First Fit RAM allocation with visual memory mapping and fragmentation stats.
- **File System**: In-memory file system with Inodes, data blocks, and directory listing.
- **Live Dashboard**: Real-time monitoring of CPU, Memory, Processes, and System Logs.
- **Modular Architecture**: Clean separation between logic and UI.

## Project Structure
```text
MiniOSKernelSimulator/
│
├── main.py                 # Entry point
├── core/                   # Kernel Logic
│   ├── kernel_simulator.py # Orchestrator
│   ├── process_manager.py
│   ├── scheduler.py
│   ├── memory_manager.py
│   ├── filesystem.py
│   ├── logger.py
│   └── constants.py
├── models/                 # Data Models
│   ├── pcb.py
│   ├── inode.py
│   └── memory_block.py
└── ui/                     # UI Layer (Rich)
    ├── dashboard.py        # Live Dashboard
    ├── menus.py            # Navigation
    └── ui_utils.py         # UI Helpers
```

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.7+ installed.

### 2. Install Dependencies
This project requires the `rich` library for the modern terminal UI.
```bash
pip install rich
```

### 3. Run the Simulator
```bash
python main.py
```

## How to Use
1. **Main Menu**: Navigate using numeric keys (1-7).
2. **Process Manager**: Create processes and see them in the PCB table.
3. **Live Dashboard**: Select option **6** to run a full system simulation with real-time updates.
4. **Memory Manager**: View the memory map and fragmentation statistics.
5. **Scheduler Info**: Check the Ready Queue and view the Gantt chart after a simulation run.
