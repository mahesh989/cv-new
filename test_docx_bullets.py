#!/usr/bin/env python3
"""
Test DOCX bullet detection directly on uploaded files
"""
import sys
import os
from pathlib import Path

# Add the backend app to the path
sys.path.append('cv-magic-app/backend')

def test_docx_bullet_detection():
    """Test bullet detection on actual uploaded DOCX files"""
    try:
        from app.services.cv_processor import CVProcessor
        
        processor = CVProcessor()
        
        # Test files from the server (Docker volume paths)
        test_files = [
            "/data/mahesh@gmail.com/cv-analysis/uploads/M_tiwari_CV_Capgemini.docx",
            "/data/mahesh@gmail.com/cv-analysis/uploads/Cv_Maheshwor_Tiwari.docx"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\n🔍 Testing: {Path(file_path).name}")
                print("=" * 50)
                
                result = processor.extract_text_from_file(Path(file_path))
                
                if result['success']:
                    text = result['text']
                    print(f"✅ Extraction successful: {len(text)} characters")
                    
                    # Count bullets
                    bullet_count = text.count('•')
                    print(f"🔹 Found {bullet_count} bullet points (•)")
                    
                    if bullet_count > 0:
                        print("\n📋 Bullet points found:")
                        lines = text.split('\n')
                        bullet_lines = [line for line in lines if '•' in line]
                        for i, line in enumerate(bullet_lines[:10]):  # Show first 10
                            print(f"  {i+1}. {line.strip()}")
                        if len(bullet_lines) > 10:
                            print(f"  ... and {len(bullet_lines) - 10} more")
                    else:
                        print("❌ No bullets found")
                        print("\n📄 First 500 characters of extracted text:")
                        print(text[:500])
                        print("...")
                        
                        # Look for potential bullet content
                        lines = text.split('\n')
                        potential_bullets = []
                        for line in lines:
                            line = line.strip()
                            if (len(line) < 200 and 
                                not line.endswith('.') and 
                                not line.endswith(':') and
                                not line.isupper() and
                                len(line) > 10):
                                potential_bullets.append(line)
                        
                        if potential_bullets:
                            print(f"\n🔍 Found {len(potential_bullets)} potential bullet lines:")
                            for i, line in enumerate(potential_bullets[:5]):
                                print(f"  {i+1}. {line}")
                else:
                    print(f"❌ Extraction failed: {result['error']}")
            else:
                print(f"❌ File not found: {file_path}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_docx_bullet_detection()
