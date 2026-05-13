from core.process_manager import ProcessManager
from core.scheduler import Scheduler
from core.memory_manager import MemoryManager
from core.filesystem import FileSystem
from core.constants import TOTAL_MEMORY, TIME_QUANTUM, SimSpeed, IO_PROBABILITY, IO_WAIT_TIME
from core.logger import Logger
from models.pcb import ProcessState
import random

class KernelSimulator:
    def __init__(self):
        self.memory_manager = MemoryManager(TOTAL_MEMORY)
        self.process_manager = ProcessManager(self.memory_manager)
        self.scheduler = Scheduler(TIME_QUANTUM)
        self.file_system = FileSystem()
        
        self.current_time = 0
        self.is_running = False

    def step(self):
        """Executes one simulation step."""
        if self.scheduler.is_idle():
            self.is_running = False
            
        # I/O Random Event Simulation
        if self.scheduler.running_process and random.random() < IO_PROBABILITY:
            reasons = ["Disk I/O", "File Read", "Keyboard Input", "Network Request"]
            reason = random.choice(reasons)
            proc = self.scheduler.running_process
            self.scheduler.put_to_waiting(proc, IO_WAIT_TIME, reason)
            self.scheduler.dispatch()

        self.current_time = self.scheduler.run_step(self.current_time)
        
        # Deallocate memory for terminated processes
        for p in self.process_manager.get_all_processes():
            if p.state == ProcessState.TERMINATED and p.memory_required > 0:
                self.memory_manager.deallocate(p.pid)
                p.memory_required = 0 # Avoid double deallocation

    def reset(self):
        self.__init__()
        Logger.clear_logs()
        Logger.log("System Reset")

    def get_status(self):
        """Returns the complete system status for JSON serialization."""
        return {
            "current_time": self.current_time,
            "is_running": self.is_running,
            "scheduler_settings": {
                "type": self.scheduler.scheduling_type,
                "quantum": self.scheduler.time_quantum
            },
            "cpu": {
                "running_process": self.scheduler.running_process.to_dict() if self.scheduler.running_process else None,
                "ready_queue": [p.to_dict() for p in self.scheduler.ready_queue],
                "waiting_queue": [
                    {**p.to_dict(), 
                     "wait_reason": self.scheduler.wait_timers[p.pid]["reason"],
                     "wait_time": self.scheduler.wait_timers[p.pid]["time"]} 
                    for p in self.scheduler.waiting_queue
                ],
                "gantt_chart": self.scheduler.gantt_chart
            },
            "memory": self.memory_manager.get_fragmentation_stats() | {
                "blocks": [b.to_dict() for b in self.memory_manager.blocks]
            },
            "processes": [p.to_dict() for p in self.process_manager.get_all_processes()],
            "files": self.file_system.get_all_files_details(),
            "logs": Logger.get_logs()[-20:] # Last 20 logs
        }
