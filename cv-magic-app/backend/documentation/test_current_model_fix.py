#!/usr/bin/env python3

"""
Test script to verify the current_model property fix
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.ai.ai_service import ai_service

def test_current_model_property():
    """Test the current_model property"""
    try:
        # Test the current_model property
        current_model = ai_service.current_model
        print(f"✅ current_model property works: {current_model}")
        
        # Test the get_current_model_name method
        current_model_method = ai_service.get_current_model_name()
        print(f"✅ get_current_model_name() method works: {current_model_method}")
        
        # Verify they return the same value
        if current_model == current_model_method:
            print("✅ Property and method return the same value")
        else:
            print(f"⚠️ Property and method return different values: {current_model} vs {current_model_method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing current_model property: {e}")
        return False

if __name__ == "__main__":
    print("Testing current_model property fix...")
    success = test_current_model_property()
    
    if success:
        print("\n🎉 Current model property fix is working!")
    else:
        print("\n❌ Current model property fix failed!")
        sys.exit(1)