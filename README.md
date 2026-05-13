# Mini OS Kernel Simulator v2.0

A visual Operating System Kernel Simulator developed for OS Laboratory coursework.  
The project demonstrates interaction between core OS components such as Process Management, CPU Scheduling, Memory Management, and File System operations.

---

## Features

- Process Creation & PCB Management
- Process State Transitions
  - NEW → READY → RUNNING → WAITING → TERMINATED
- Round Robin Scheduling
- Priority Scheduling (Preemptive)
- Configurable Time Quantum
- Memory Allocation & Deallocation
- Fragmentation Visualization
- Waiting (I/O) Queue Simulation
- File System Operations
  - Create
  - Read
  - Write/Edit
  - Delete
- Inode Table Visualization
- Event Logs with Timestamps
- Execution Gantt Chart

---

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript

---

## How to Run

```bash
pip install -r requirements.txt
python app.py
