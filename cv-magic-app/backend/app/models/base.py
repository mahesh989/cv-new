"""
Shared database base class for all models
"""
from sqlalchemy.ext.declarative import declarative_base

# Single shared base class for all models
Base = declarative_base()
