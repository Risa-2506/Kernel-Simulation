# Global System Constants
TOTAL_MEMORY = 1024      # Total RAM in KB
TIME_QUANTUM = 2        # Default Round Robin Time Quantum
DEFAULT_PROCESS_PRIORITY = 1

# Simulation Speeds (seconds sleep)
class SimSpeed:
    SLOW = 1.5
    NORMAL = 0.8
    FAST = 0.2

# Scheduling Types
class SchedulingType:
    ROUND_ROBIN = "Round Robin"
    PRIORITY = "Priority (Preemptive)"

# I/O Simulation
IO_PROBABILITY = 0.2  # 20% chance to enter WAITING state per step
IO_WAIT_TIME = 3      # Time steps spent in WAITING
