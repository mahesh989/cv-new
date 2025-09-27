"""
Admin routes for user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from app.models.auth import UserData, UserResponse
from app.core.dependencies import get_admin_user
from app.database import get_database
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(admin_user: UserData = Depends(get_admin_user)):
    """List all users (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    users = user_service.get_all_users()
    return [user_service.to_user_response(user) for user in users]


@router.get("/users/active", response_model=List[UserResponse])
async def list_active_users(admin_user: UserData = Depends(get_admin_user)):
    """List all active users (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    users = user_service.get_active_users()
    return [user_service.to_user_response(user) for user in users]


@router.get("/users/admins", response_model=List[UserResponse])
async def list_admin_users(admin_user: UserData = Depends(get_admin_user)):
    """List all admin users (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    users = user_service.get_admin_users()
    return [user_service.to_user_response(user) for user in users]


@router.get("/system-stats")
async def get_system_stats(admin_user: UserData = Depends(get_admin_user)):
    """Get system statistics (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    total_users = len(user_service.get_all_users())
    active_users = len(user_service.get_active_users())
    admin_users = len(user_service.get_admin_users())
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "inactive_users": total_users - active_users
    }


@router.post("/users/{user_id}/activate")
async def activate_user(user_id: int, admin_user: UserData = Depends(get_admin_user)):
    """Activate user account (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    success = user_service.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} activated successfully"}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, admin_user: UserData = Depends(get_admin_user)):
    """Deactivate user account (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    success = user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} deactivated successfully"}


@router.post("/users/{user_id}/make-admin")
async def make_admin(user_id: int, admin_user: UserData = Depends(get_admin_user)):
    """Make user an admin (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    success = user_service.make_admin(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User {user_id} is now an admin"}


@router.post("/users/{user_id}/remove-admin")
async def remove_admin(user_id: int, admin_user: UserData = Depends(get_admin_user)):
    """Remove admin privileges (admin only)"""
    db = next(get_database())
    user_service = UserService(db)
    
    success = user_service.remove_admin(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"Admin privileges removed from user {user_id}"}
