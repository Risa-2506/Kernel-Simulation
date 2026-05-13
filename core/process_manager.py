from typing import List, Optional
from models.pcb import PCB, ProcessState
from core.memory_manager import MemoryManager
from core.logger import Logger

class ProcessManager:
    def __init__(self, memory_manager: MemoryManager):
        self.processes: List[PCB] = []
        self.memory_manager = memory_manager
        self.next_pid = 1001

    def create_process(self, name: str, priority: int, burst_time: int, memory_required: int) -> bool:
        if self.memory_manager.allocate(self.next_pid, memory_required):
            new_process = PCB(
                pid=self.next_pid,
                name=name,
                priority=priority,
                arrival_time=0,
                burst_time=burst_time,
                remaining_burst_time=burst_time,
                memory_required=memory_required
            )
            self.processes.append(new_process)
            Logger.log(f"Process created: {name} (PID: {self.next_pid})")
            self.next_pid += 1
            return True
        else:
            Logger.log(f"Failed to create process {name}: Insufficient memory")
            return False

    def terminate_process(self, pid: int):
        for p in self.processes:
            if p.pid == pid and p.state != ProcessState.TERMINATED:
                p.state = ProcessState.TERMINATED
                self.memory_manager.deallocate(pid)
                Logger.log(f"Process terminated: {p.name} (PID: {pid})")
                return

    def get_process_by_id(self, pid: int) -> Optional[PCB]:
        for p in self.processes:
            if p.pid == pid:
                return p
        return None

    def get_all_processes(self) -> List[PCB]:
        return self.processes

    def get_process_count(self) -> int:
        return len(self.processes)
