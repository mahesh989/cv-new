#!/usr/bin/env python3
"""
Script to recreate database tables with new schema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models.user import User
from app.models.cv import CV, JobApplication, CVAnalysis, JobComparison
from app.models.user import UserSession
from app.models.user_data import UserAPIKey, UserSettings, UserFileStorage, UserActivityLog

def recreate_tables():
    """Recreate all database tables"""
    print("🗑️  Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 Creating new tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables recreated successfully!")

if __name__ == "__main__":
    try:
        recreate_tables()
        print("🎉 Database migration completed successfully!")
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        sys.exit(1)
