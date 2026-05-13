from dataclasses import dataclass, field
from typing import List

@dataclass
class Inode:
    inode_number: int
    filename: str
    file_size: int
    content: str
    data_blocks: List[int] = field(default_factory=list)
