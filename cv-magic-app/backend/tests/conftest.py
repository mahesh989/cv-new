"""
Pytest configuration file for shared fixtures and settings
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))