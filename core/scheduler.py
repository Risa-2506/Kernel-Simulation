from collections import deque
from typing import List, Optional, Dict
from models.pcb import PCB, ProcessState
from core.logger import Logger
from core.constants import SchedulingType

class Scheduler:
    def __init__(self, time_quantum: int):
        self.ready_queue: deque[PCB] = deque()
        self.waiting_queue: List[PCB] = []
        self.running_process: Optional[PCB] = None
        self.time_quantum = time_quantum
        self.scheduling_type = SchedulingType.ROUND_ROBIN
        self.gantt_chart: List[Dict] = []
        self.wait_timers: Dict[int, int] = {} 

    def enqueue(self, process: PCB):
        if process.state != ProcessState.TERMINATED:
            process.state = ProcessState.READY
            self.ready_queue.append(process)
            Logger.log(f"Process P{process.pid} added to READY queue", "scheduling")

    def dispatch(self) -> Optional[PCB]:
        if not self.ready_queue:
            self.running_process = None
            return None
        
        if self.scheduling_type == SchedulingType.PRIORITY:
            # SMALLER NUMBER = HIGHER PRIORITY
            highest_prio_idx = 0
            for i in range(1, len(self.ready_queue)):
                if self.ready_queue[i].priority < self.ready_queue[highest_prio_idx].priority:
                    highest_prio_idx = i
            
            proc_list = list(self.ready_queue)
            self.running_process = proc_list.pop(highest_prio_idx)
            self.ready_queue = deque(proc_list)
        else:
            self.running_process = self.ready_queue.popleft()
            
        self.running_process.state = ProcessState.RUNNING
        Logger.log(f"Scheduler selected P{self.running_process.pid} for execution", "scheduling")
        return self.running_process

    def put_to_waiting(self, process: PCB, wait_time: int, reason: str = "Disk I/O"):
        process.state = ProcessState.WAITING
        self.waiting_queue.append(process)
        self.wait_timers[process.pid] = {
            "time": wait_time,
            "reason": reason
        }
        self.running_process = None
        Logger.log(f"P{process.pid} requested {reason} and moved to WAITING state", "waiting")

    def update_waiting_processes(self):
        to_ready = []
        for p in self.waiting_queue:
            timer_data = self.wait_timers[p.pid]
            timer_data["time"] -= 1
            if timer_data["time"] <= 0:
                to_ready.append(p)
        
        for p in to_ready:
            reason = self.wait_timers[p.pid]["reason"]
            self.waiting_queue.remove(p)
            del self.wait_timers[p.pid]
            self.enqueue(p)
            Logger.log(f"{reason} completed for P{p.pid}. Process returned to READY queue", "success")

    def run_step(self, current_time: int) -> int:
        self.update_waiting_processes()

        # Preemptive Priority Check (only if in Priority mode)
        if self.scheduling_type == SchedulingType.PRIORITY and self.running_process and self.ready_queue:
            highest_in_queue = min(self.ready_queue, key=lambda x: x.priority)
            if highest_in_queue.priority < self.running_process.priority:
                Logger.log(f"Preemption: Higher priority P{highest_in_queue.pid} (Prio {highest_in_queue.priority}) takes over from P{self.running_process.pid} (Prio {self.running_process.priority})", "scheduling")
                self.running_process.state = ProcessState.READY
                self.ready_queue.append(self.running_process)
                self.running_process = None

        # Dispatch if idle
        if not self.running_process:
            self.dispatch()

        if self.running_process:
            # Calculate execution time for this turn (Respects quantum for both RR and Priority per user request)
            exec_time = min(self.time_quantum, self.running_process.remaining_burst_time)
            
            start_time = current_time
            self.running_process.remaining_burst_time -= exec_time
            current_time += exec_time
            
            # Gantt Chart Update: Proper block per turn
            self.gantt_chart.append({
                "name": self.running_process.name,
                "start": start_time,
                "end": current_time,
                "duration": exec_time
            })
            
            if self.running_process.remaining_burst_time <= 0:
                self.running_process.state = ProcessState.TERMINATED
                Logger.log(f"P{self.running_process.pid} finished execution at T={current_time}", "termination")
                self.running_process = None
                self.dispatch()
            elif self.scheduling_type == SchedulingType.ROUND_ROBIN:
                Logger.log(f"P{self.running_process.pid} executed for {exec_time} CPU units. Quantum expired.", "scheduling")
                self.running_process.state = ProcessState.READY
                self.ready_queue.append(self.running_process)
                self.running_process = None
                self.dispatch()
            # In Priority mode, if not terminated, it stays running for next step unless preempted
        
        return current_time

    def is_idle(self) -> bool:
        return not self.ready_queue and self.running_process is None and not self.waiting_queue
