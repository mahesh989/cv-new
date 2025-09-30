"""Path Debugging Utility

This module provides utilities for debugging file paths and structure during analysis.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PathDebug:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._indent = 0
        
    def _log(self, message: str):
        if self.enabled:
            indent = "  " * self._indent
            logger.info(f"{indent}{message}")
    
    def start_operation(self, name: str):
        """Start a new operation block"""
        self._log(f"\n📌 Starting {name}")
        self._indent += 1
        return self
    
    def end_operation(self):
        """End the current operation block"""
        self._indent -= 1
        if self._indent < 0:
            self._indent = 0
        return self
    
    def log_path(self, path: Path, description: str = ""):
        """Log a path with optional description"""
        if description:
            self._log(f"📂 {description}: {path}")
        else:
            self._log(f"📂 Path: {path}")
        return self
    
    def verify_path(self, path: Path, expected_pattern: str) -> bool:
        """Verify a path matches expected pattern"""
        path_str = str(path)
        match = expected_pattern in path_str
        if match:
            self._log(f"✅ Path valid: {path}")
        else:
            self._log(f"❌ Invalid path: {path}")
            self._log(f"   Expected pattern: {expected_pattern}")
        return match
    
    def check_file_content(self, file_path: Path, required_fields: Optional[list] = None):
        """Check if a file exists and has required fields"""
        if not file_path.exists():
            self._log(f"❌ File missing: {file_path}")
            return False
            
        try:
            with open(file_path) as f:
                data = json.load(f)
                
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    self._log(f"❌ Missing fields in {file_path.name}: {missing}")
                    return False
                else:
                    self._log(f"✅ File complete: {file_path.name}")
            else:
                self._log(f"✅ File exists: {file_path.name}")
            return True
            
        except Exception as e:
            self._log(f"❌ Error reading {file_path}: {e}")
            return False
    
    def print_file_tree(self, base_path: Path, max_depth: int = 3):
        """Print a tree view of files under base_path"""
        self._log("\n📁 File structure:")
        self._print_tree(base_path, "", max_depth)
        return self
        
    def _print_tree(self, path: Path, prefix: str, max_depth: int, current_depth: int = 0):
        """Helper for print_file_tree"""
        if current_depth > max_depth:
            return
            
        if not path.exists():
            self._log(f"{prefix}❌ {path.name} (missing)")
            return
            
        if path.is_file():
            self._log(f"{prefix}📄 {path.name}")
        else:
            self._log(f"{prefix}📁 {path.name}/")
            
            try:
                children = sorted(path.iterdir())
                for i, child in enumerate(children):
                    is_last = i == len(children) - 1
                    new_prefix = prefix + ("└── " if is_last else "├── ")
                    self._print_tree(child, new_prefix, max_depth, current_depth + 1)
            except Exception as e:
                self._log(f"{prefix}❌ Error listing directory: {e}")

# Create global instance
path_debug = PathDebug()