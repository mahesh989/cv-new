"""
Email authentication routes for verification and password reset
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.models.auth import UserData, UserResponse, EmailVerificationRequest, PasswordResetRequest, PasswordResetConfirm
from app.core.dependencies import get_current_user
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from app.database import get_database

router = APIRouter(prefix="/auth", tags=["email-auth"])
security = HTTPBearer()


@router.post("/send-verification")
async def send_verification_email(current_user: UserData = Depends(get_current_user)):
    """Send email verification to authenticated user"""
    try:
        if current_user.is_verified:
            return {"message": "Email is already verified"}
        
        # Generate verification token
        token_service = TokenService()
        verification_token = token_service.generate_verification_token(
            int(current_user.id), current_user.email
        )
        
        # Send verification email
        email_service = EmailService()
        success = email_service.send_verification_email(
            current_user.email, 
            current_user.name, 
            verification_token
        )
        
        if success:
            return {"message": "Verification email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/verify-email")
async def verify_email(request: EmailVerificationRequest):
    """Verify email with token"""
    try:
        token_service = TokenService()
        result = token_service.verify_email_token(request.token)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Send welcome email
        email_service = EmailService()
        email_service.send_welcome_email(result["email"], result["username"])
        
        return {
            "message": "Email verified successfully",
            "user": {
                "id": result["user_id"],
                "email": result["email"],
                "username": result["username"],
                "is_verified": result["is_verified"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Send password reset email"""
    try:
        # Find user by email
        db = next(get_database())
        user_service = UserService(db)
        user = user_service.get_user_by_email(request.email)
        
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Generate reset token
        token_service = TokenService()
        reset_token = token_service.generate_reset_token(user.id, user.email)
        
        # Send reset email
        email_service = EmailService()
        success = email_service.send_password_reset_email(
            user.email, 
            user.username, 
            reset_token
        )
        
        if success:
            return {"message": "If the email exists, a password reset link has been sent"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process password reset request: {str(e)}"
        )


@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with token"""
    try:
        # Verify reset token
        token_service = TokenService()
        result = token_service.verify_reset_token(request.token)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        db = next(get_database())
        user_service = UserService(db)
        user = user_service.get_user_by_id(result["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Set new password
        user.set_password(request.new_password)
        db.commit()
        
        # Invalidate reset token
        token_service.invalidate_reset_token(request.token)
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.get("/verification-status")
async def get_verification_status(current_user: UserData = Depends(get_current_user)):
    """Get email verification status for authenticated user"""
    try:
        return {
            "is_verified": current_user.is_verified,
            "email": current_user.email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get verification status: {str(e)}"
        )


@router.post("/resend-verification")
async def resend_verification_email(current_user: UserData = Depends(get_current_user)):
    """Resend verification email"""
    try:
        if current_user.is_verified:
            return {"message": "Email is already verified"}
        
        # Generate new verification token
        token_service = TokenService()
        verification_token = token_service.generate_verification_token(
            int(current_user.id), current_user.email
        )
        
        # Send verification email
        email_service = EmailService()
        success = email_service.send_verification_email(
            current_user.email, 
            current_user.name, 
            verification_token
        )
        
        if success:
            return {"message": "Verification email resent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resend verification email"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}"
        )
