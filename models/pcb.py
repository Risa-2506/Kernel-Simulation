from dataclasses import dataclass
from enum import Enum

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

@dataclass
class PCB:
    pid: int
    name: str
    priority: int
    arrival_time: int
    burst_time: int
    remaining_burst_time: int
    memory_required: int
    state: ProcessState = ProcessState.NEW

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "priority": self.priority,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "remaining_burst_time": self.remaining_burst_time,
            "memory_required": self.memory_required,
            "state": self.state.value
        }
