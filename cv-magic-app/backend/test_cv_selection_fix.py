#!/usr/bin/env python3
"""
Test script to verify the CV selection fix.
This tests that when original_cv is newer than tailored CVs, it gets selected first.
"""

import sys
import os
from pathlib import Path
import time
import tempfile
import shutil

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_cv_selection_logic():
    """Test that original_cv is selected when it's significantly newer than tailored CVs"""
    
    print("=" * 80)
    print("Testing CV Selection Logic Fix")
    print("=" * 80)
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create directory structure
        user_dir = tmppath / "user" / "test@example.com" / "cv-analysis"
        cvs_dir = user_dir / "cvs"
        original_dir = cvs_dir / "original"
        tailored_dir = cvs_dir / "tailored"
        
        original_dir.mkdir(parents=True, exist_ok=True)
        tailored_dir.mkdir(parents=True, exist_ok=True)
        
        # Create an old tailored CV (simulating Oct 26 Foodbank CV)
        old_tailored_json = tailored_dir / "TestCompany_tailored_cv_20251026_103852.json"
        old_tailored_txt = tailored_dir / "TestCompany_tailored_cv_20251026_103852.txt"
        
        old_tailored_json.write_text('{"name": "Old Tailored CV"}')
        old_tailored_txt.write_text('Old Tailored CV Content')
        
        # Set old modification time (Oct 26)
        old_time = time.time() - (4 * 24 * 3600)  # 4 days ago
        os.utime(old_tailored_json, (old_time, old_time))
        os.utime(old_tailored_txt, (old_time, old_time))
        
        print(f"✅ Created old tailored CV: {old_tailored_json.name}")
        print(f"   Modified: {old_time} ({time.ctime(old_time)})")
        
        # Wait a moment
        time.sleep(0.1)
        
        # Create a new original CV (simulating fresh upload)
        original_json = original_dir / "original_cv.json"
        original_txt = original_dir / "original_cv.txt"
        
        original_json.write_text('{"name": "New Original CV - Maheshwor Tiwari"}')
        original_txt.write_text('New Original CV - Maheshwor Tiwari Content')
        
        new_time = time.time()
        os.utime(original_json, (new_time, new_time))
        os.utime(original_txt, (new_time, new_time))
        
        print(f"✅ Created new original CV: {original_json.name}")
        print(f"   Modified: {new_time} ({time.ctime(new_time)})")
        print(f"   Time difference: {new_time - old_time:.0f} seconds")
        
        # Now test the selection logic
        print("\n" + "=" * 80)
        print("Testing CV Selection...")
        print("=" * 80)
        
        # Temporarily set up the path for testing by mocking the user_path_utils
        import app.utils.user_path_utils as upu
        original_get_user_base_path = upu.get_user_base_path
        
        def mock_get_user_base_path(email):
            return user_dir
        
        upu.get_user_base_path = mock_get_user_base_path
        
        try:
            from app.unified_latest_file_selector import UnifiedLatestFileSelector
            
            # Create selector with test user
            selector = UnifiedLatestFileSelector(user_email="test@example.com")
            
            result = selector.get_latest_cv_across_all("TestCompany")
            
            print(f"\n📊 Selection Result:")
            print(f"   Type: {result.file_type}")
            print(f"   JSON Path: {result.json_path}")
            print(f"   TXT Path: {result.txt_path}")
            print(f"   Timestamp: {result.timestamp}")
            
            # Verify the result
            if result.file_type == "original":
                print("\n✅ SUCCESS: Original CV was selected (as expected)")
                print("   The fix is working correctly!")
                return True
            else:
                print("\n❌ FAILURE: Tailored CV was selected (unexpected)")
                print("   The fix is NOT working correctly.")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Restore original function
            upu.get_user_base_path = original_get_user_base_path

if __name__ == "__main__":
    success = test_cv_selection_logic()
    sys.exit(0 if success else 1)

