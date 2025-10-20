#!/usr/bin/env python3
"""
Debug AI Service Configuration
"""

import asyncio
import sys
import os
sys.path.append('/app')

from app.ai.ai_service import AIServiceManager
from app.database import get_db
from app.models.auth import User, UserAPIKey
from sqlalchemy.orm import Session

async def debug_ai_service():
    print("🔍 DEBUGGING AI SERVICE CONFIGURATION")
    print("=" * 50)
    
    # Test database connection
    print("1. Testing database connection...")
    try:
        db = next(get_db())
        users = db.query(User).filter(User.email == "mahesh@gmail.com").all()
        print(f"   ✅ Found {len(users)} users with email mahesh@gmail.com")
        
        if users:
            user = users[0]
            print(f"   ✅ User ID: {user.id}, Email: {user.email}")
            
            # Check API keys
            api_keys = db.query(UserAPIKey).filter(UserAPIKey.user_id == str(user.id)).all()
            print(f"   ✅ Found {len(api_keys)} API keys for user {user.id}")
            
            for key in api_keys:
                print(f"      - Provider: {key.provider}, Valid: {key.is_valid}")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Test AI Service Manager
    print("\n2. Testing AI Service Manager...")
    try:
        ai_service = AIServiceManager()
        print(f"   ✅ AI Service Manager created")
        print(f"   ✅ Available providers: {ai_service.available_providers}")
        print(f"   ✅ Current provider: {ai_service.current_provider}")
        
        # Test with user
        if users:
            user = users[0]
            print(f"\n3. Testing AI Service with user {user.email} (ID: {user.id})...")
            
            # Try to get a provider for the user
            provider = ai_service.get_provider_for_user(user)
            print(f"   ✅ Provider for user: {provider}")
            
            if provider:
                print(f"   ✅ Provider name: {provider.name}")
                print(f"   ✅ Provider configured: {provider.is_configured}")
            else:
                print(f"   ❌ No provider found for user")
        
    except Exception as e:
        print(f"   ❌ AI Service error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ai_service())
