from dataclasses import dataclass

@dataclass
class MemoryBlock:
    start: int
    size: int
    free: bool
    pid: int = -1 # PID of process using it, -1 if free

    def to_dict(self):
        return {
            "start": self.start,
            "size": self.size,
            "free": self.free,
            "pid": self.pid
        }
