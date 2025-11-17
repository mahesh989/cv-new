#!/usr/bin/env python3
import sys
import asyncio
import os
sys.path.append('/app')

async def test_actual_cv_generation():
    print('🧪 TESTING ACTUAL CV GENERATION')
    print('=' * 50)
    
    try:
        from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
        from app.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        user = db.query(User).filter(User.email == 'munna@gmail.com').first()
        print(f'User: {user.email}')
        
        print('Testing CV tailoring for Australia_for_UNHCR...')
        service = CVTailoringService(user.email)
        result = await service.tailor_cv('Australia_for_UNHCR')
        print('✅ CV tailoring completed successfully!')
        
        from pathlib import Path
        user_path = Path('/app/user/munna@gmail.com/cv-analysis')
        tailored_files = list(user_path.rglob('*tailored*'))
        
        print(f'Tailored CV files found: {len(tailored_files)}')
        for file in tailored_files:
            print(f'  - {file}')
        
        db.close()
        return True
        
    except Exception as e:
        print(f'❌ CV tailoring failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_actual_cv_generation())
    if success:
        print('🎉 CV generation test completed!')
    else:
        print('❌ CV generation test failed!')
        sys.exit(1)
