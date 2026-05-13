from typing import List
from models.memory_block import MemoryBlock
from core.logger import Logger

class MemoryManager:
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size, True)]

    def allocate(self, pid: int, size: int) -> bool:
        # First Fit Allocation
        for i, block in enumerate(self.blocks):
            if block.free and block.size >= size:
                remaining_size = block.size - size
                block.size = size
                block.free = False
                block.pid = pid

                if remaining_size > 0:
                    new_block = MemoryBlock(block.start + size, remaining_size, True)
                    self.blocks.insert(i + 1, new_block)
                
                Logger.log(f"Memory allocated: {size}KB to P{pid}")
                return True
        return False

    def deallocate(self, pid: int):
        for i, block in enumerate(self.blocks):
            if not block.free and block.pid == pid:
                block.free = True
                block.pid = -1
                Logger.log(f"Memory released from P{pid}")

                # Merge with next block if free
                if i + 1 < len(self.blocks) and self.blocks[i+1].free:
                    block.size += self.blocks[i+1].size
                    self.blocks.pop(i + 1)
                
                # Merge with previous block if free
                if i > 0 and self.blocks[i-1].free:
                    self.blocks[i-1].size += block.size
                    self.blocks.pop(i)
                return

    def get_total_free_memory(self) -> int:
        return sum(block.size for block in self.blocks if block.free)

    def get_largest_free_block(self) -> int:
        free_blocks = [block.size for block in self.blocks if block.free]
        return max(free_blocks) if free_blocks else 0

    def get_memory_usage(self) -> int:
        return self.total_size - self.get_total_free_memory()

    def get_fragmentation_stats(self):
        free_blocks = [b for b in self.blocks if b.free]
        used_mem = self.get_memory_usage()
        
        # External fragmentation is approximated by (1 - largest_free / total_free) * 100
        total_free = self.get_total_free_memory()
        largest_free = self.get_largest_free_block()
        frag_percent = 0
        if total_free > 0:
            frag_percent = (1 - (largest_free / total_free)) * 100

        return {
            "total": self.total_size,
            "used": used_mem,
            "free": total_free,
            "largest_free": largest_free,
            "free_holes": len(free_blocks),
            "frag_percent": round(frag_percent, 2)
        }
