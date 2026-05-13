from typing import Dict, Optional
from models.inode import Inode
from core.logger import Logger
from datetime import datetime

class FileSystem:
    def __init__(self):
        self.files: Dict[str, Inode] = {}
        self.next_inode = 1
        self.creation_times: Dict[str, str] = {}

    def create_file(self, name: str, content: str) -> bool:
        if name in self.files:
            Logger.log(f"Error: File {name} already exists", "error")
            return False
        
        file_size = len(content)
        num_blocks = max(1, (file_size // 4) + (1 if file_size % 4 != 0 else 0))
        # Start blocks from 100, 200, 300 etc based on inode
        data_blocks = [self.next_inode * 100 + i for i in range(num_blocks)]
        
        new_file = Inode(
            inode_number=self.next_inode,
            filename=name,
            file_size=file_size,
            content=content,
            data_blocks=data_blocks
        )
        
        self.files[name] = new_file
        self.creation_times[name] = datetime.now().strftime("%H:%M:%S")
        self.next_inode += 1
        Logger.log(f"File created: {name} ({file_size} bytes, {num_blocks} blocks)", "success")
        return True

    def edit_file(self, name: str, new_content: str) -> bool:
        if name not in self.files:
            Logger.log(f"Error: File {name} not found", "error")
            return False
        
        inode = self.files[name]
        inode.content = new_content
        inode.file_size = len(new_content)
        
        # Update blocks if size changed
        num_blocks = max(1, (inode.file_size // 4) + (1 if inode.file_size % 4 != 0 else 0))
        if len(inode.data_blocks) != num_blocks:
            inode.data_blocks = [inode.inode_number * 100 + i for i in range(num_blocks)]
            
        Logger.log(f"File edited: {name} (New size: {inode.file_size} bytes, {num_blocks} blocks)", "success")
        return True

    def delete_file(self, name: str) -> bool:
        if name in self.files:
            del self.files[name]
            del self.creation_times[name]
            Logger.log(f"File deleted: {name}")
            return True
        Logger.log(f"Error: File {name} not found")
        return False

    def read_file(self, name: str) -> str:
        if name in self.files:
            return self.files[name].content
        return "Error: File not found"

    def get_file_details(self, name: str):
        if name in self.files:
            f = self.files[name]
            return {
                "inode_number": f.inode_number,
                "filename": f.filename,
                "file_size": f.file_size,
                "content": f.content,
                "data_blocks": f.data_blocks,
                "created_at": self.creation_times[name]
            }
        return None

    def get_all_files_details(self):
        return [self.get_file_details(name) for name in self.files]
