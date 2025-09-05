import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel

from ..config.logging import logger


class FileInfo(BaseModel):
    name: str
    path: str
    size: int
    extension: str
    exists: bool


class FileOperationsTool:
    """File operations tool for agents"""
    
    def __init__(self, allowed_extensions: Optional[List[str]] = None, max_size_mb: int = 100):
        self.allowed_extensions = allowed_extensions or [".txt", ".json", ".csv", ".md", ".py"]
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def get_file_info(self, file_path: str) -> FileInfo:
        """Get information about a file"""
        path = Path(file_path)
        
        return FileInfo(
            name=path.name,
            path=str(path.absolute()),
            size=path.stat().st_size if path.exists() else 0,
            extension=path.suffix,
            exists=path.exists()
        )
    
    async def read_text_file(self, file_path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read a text file safely"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return None
            
            if path.suffix not in self.allowed_extensions:
                logger.error(f"File extension not allowed: {path.suffix}")
                return None
            
            if path.stat().st_size > self.max_size_bytes:
                logger.error(f"File too large: {path.stat().st_size} bytes")
                return None
            
            content = path.read_text(encoding=encoding)
            logger.info(f"Successfully read file: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def write_text_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to a text file safely"""
        try:
            path = Path(file_path)
            
            if path.suffix not in self.allowed_extensions:
                logger.error(f"File extension not allowed: {path.suffix}")
                return False
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            path.write_text(content, encoding=encoding)
            logger.info(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    async def read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read and parse a JSON file"""
        content = await self.read_text_file(file_path)
        if content is None:
            return None
        
        try:
            data = json.loads(content)
            logger.info(f"Successfully parsed JSON file: {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            return None
    
    async def write_json_file(self, file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """Write data to a JSON file"""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return await self.write_text_file(file_path, content)
        except Exception as e:
            logger.error(f"Error serializing data for {file_path}: {e}")
            return False
    
    async def list_directory(self, directory_path: str, pattern: str = "*") -> List[FileInfo]:
        """List files in a directory"""
        try:
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                logger.error(f"Directory does not exist or is not a directory: {directory_path}")
                return []
            
            files = []
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    files.append(self.get_file_info(str(file_path)))
            
            logger.info(f"Listed {len(files)} files in {directory_path}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            return []
    
    async def download_file(self, url: str, file_path: str, timeout: int = 30) -> bool:
        """Download a file from a URL"""
        try:
            path = Path(file_path)
            
            if path.suffix not in self.allowed_extensions:
                logger.error(f"File extension not allowed: {path.suffix}")
                return False
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                if len(response.content) > self.max_size_bytes:
                    logger.error(f"Downloaded file too large: {len(response.content)} bytes")
                    return False
                
                # Create directory if it doesn't exist
                path.parent.mkdir(parents=True, exist_ok=True)
                
                path.write_bytes(response.content)
                logger.info(f"Successfully downloaded file from {url} to {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            return False


# Global tool instance
file_operations_tool = FileOperationsTool()