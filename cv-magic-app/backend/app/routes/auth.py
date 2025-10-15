"""
Authentication routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from app.models.auth import LoginRequest, TokenResponse, UserData, RegisterRequest, RegisterResponse
from app.core.auth import authenticate_user, create_access_token, create_refresh_token
from app.core.dependencies import get_current_user
from app.config import settings
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_database
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest, db: Session = Depends(get_database)):
    """Register a new user account"""
    logger.info(f"🔵 [REGISTER] Starting registration process")
    logger.info(f"🔵 [REGISTER] Raw payload: {payload}")
    logger.info(f"🔵 [REGISTER] Email: '{payload.email}', Name: '{payload.name}', Password length: {len(payload.password) if payload.password else 0}")
    
    try:
        # Normalize email and validate
        email = payload.email.strip().lower()
        logger.info(f"🔵 [REGISTER] Normalized email: '{email}'")
        
        if not email or len(email) < 5:
            logger.warning(f"🔴 [REGISTER] Invalid email: '{email}' (length: {len(email)})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address"
            )

        # Validate password
        password = payload.password
        logger.info(f"🔵 [REGISTER] Password validation - length: {len(password) if password else 0}")
        if not password or len(password) < 6:
            logger.warning(f"🔴 [REGISTER] Password too short: {len(password) if password else 0} characters")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )

        # Check if user already exists
        logger.info(f"🔵 [REGISTER] Checking if user exists: '{email}'")
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            logger.warning(f"🔴 [REGISTER] User already exists: '{email}' (ID: {existing.id})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists. Please sign in instead."
            )
        logger.info(f"🔵 [REGISTER] User does not exist, proceeding with creation")

        # Generate unique username
        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        logger.info(f"🔵 [REGISTER] Base username: '{base_username}'")
        
        # Check if username already exists and generate unique one
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
            logger.info(f"🔵 [REGISTER] Username conflict, trying: '{username}'")
        
        logger.info(f"🔵 [REGISTER] Final username: '{username}'")
        
        # Create new user
        logger.info(f"🔵 [REGISTER] Creating user object")
        user = User(
            username=username,
            email=email,
            full_name=payload.name,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        logger.info(f"🔵 [REGISTER] Setting password")
        user.set_password(password)

        try:
            logger.info(f"🔵 [REGISTER] Adding user to database")
            db.add(user)
            logger.info(f"🔵 [REGISTER] Committing to database")
            db.commit()
            logger.info(f"🔵 [REGISTER] Refreshing user object")
            db.refresh(user)
            logger.info(f"🔵 [REGISTER] User created successfully with ID: {user.id}")
        except Exception as db_error:
            logger.error(f"🔴 [REGISTER] Database error: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user account: {str(db_error)}"
            )

        # Ensure user-specific directories exist
        try:
            logger.info(f"🔵 [REGISTER] Creating user directories for: {user.email}")
            from app.utils.user_path_utils import ensure_user_directories
            ensure_user_directories(user.email)
            logger.info(f"🔵 [REGISTER] User directories created successfully")
        except Exception as dir_error:
            # Log error but don't fail registration
            logger.error(f"🔴 [REGISTER] Failed to create user directories: {str(dir_error)}")

        # Return success response without tokens
        logger.info(f"🔵 [REGISTER] Preparing success response")
        response = RegisterResponse(
            message="Account created successfully. Please sign in.",
            user_id=str(user.id),
            email=user.email,
            success=True
        )

        logger.info(f"✅ [REGISTER] User registered successfully: {user.email} (ID: {user.id})")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_database)):
    """
    User login endpoint
    
    Args:
        credentials: Login credentials (email and password, both can be empty)
        
    Returns:
        TokenResponse with access token and user data
    """
    logger.info(f"🔵 [LOGIN] Starting login process")
    logger.info(f"🔵 [LOGIN] Raw credentials: {credentials}")
    logger.info(f"🔵 [LOGIN] Email: '{credentials.email}', Password length: {len(credentials.password) if credentials.password else 0}")
    
    # Authenticate user (checks DB; admin fallback supported)
    logger.info(f"🔵 [LOGIN] Attempting authentication")
    user = authenticate_user(credentials.email, credentials.password, db)
    
    if not user:
        logger.warning(f"🔴 [LOGIN] Authentication failed for email: '{credentials.email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"🔵 [LOGIN] Authentication successful for user: {user.email} (ID: {user.id})")
    
    # Ensure user-specific directories exist immediately on login
    logger.info(f"🔵 [LOGIN] Ensuring user directories exist for: {user.email}")
    from app.utils.user_path_utils import ensure_user_directories
    # Enforce user directory creation; raise error on failure
    base_path = ensure_user_directories(user.email)
    if not base_path or not base_path.exists():
        logger.error(f"🔴 [LOGIN] Failed to create user directories for: {user.email}")
        raise HTTPException(status_code=500, detail="Failed to initialize user storage directories")
    logger.info(f"🔵 [LOGIN] User directories verified/created successfully")

    # Create tokens
    logger.info(f"🔵 [LOGIN] Creating JWT tokens")
    user_dict = {"id": user.id, "email": user.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user.id)
    logger.info(f"🔵 [LOGIN] Tokens created successfully")
    
    # Return token response
    logger.info(f"✅ [LOGIN] Login successful for user: {user.email} (ID: {user.id})")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,  # Convert to seconds
        user=user
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout endpoint"""
    return {"message": "Logout endpoint - to be implemented"}


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token endpoint"""
    return {"message": "Token refresh endpoint - to be implemented"}


@router.get("/profile", response_model=UserData)
async def get_profile(current_user: UserData = Depends(get_current_user)):
    """
    Get user profile endpoint
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile data
    """
    return current_user


@router.put("/profile")
async def update_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update user profile endpoint"""
    return {"message": "Profile update endpoint - to be implemented"}


@router.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Debug endpoint to check token status"""
    from app.core.auth import verify_token
    try:
        token_data = verify_token(credentials.credentials)
        return {
            "status": "valid",
            "user_id": token_data.user_id,
            "email": token_data.email,
            "expires_at": token_data.exp.isoformat(),
            "issued_at": token_data.iat.isoformat()
        }
    except HTTPException as e:
        return {
            "status": "invalid",
            "error": e.detail,
            "status_code": e.status_code
        }


@router.post("/refresh-session")
async def refresh_session():
    """Create a new session token for development"""
    from app.core.auth import create_demo_user, create_access_token, create_refresh_token
    from app.models.auth import TokenResponse
    
    # Create a fresh demo user and tokens
    user = create_demo_user()
    user_dict = {"id": user.id, "email": user.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=user
    )


@router.post("/refresh-token")
async def refresh_token(request: Request, db: Session = Depends(get_database)):
    """Refresh access token using refresh token"""
    from app.core.auth import verify_token, create_access_token, create_refresh_token
    from app.models.auth import TokenResponse
    from app.core.dependencies import get_user_by_id
    
    try:
        # Get refresh token from request body or Authorization header
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Verify refresh token
        token_data = verify_token(refresh_token)
        
        # Check if it's actually a refresh token
        import jwt
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user from database
        user = get_user_by_id(db, token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        user_dict = {"id": str(user.id), "email": user.email}
        new_access_token = create_access_token(user_dict)
        new_refresh_token = create_refresh_token(str(user.id))
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
            user=UserData(id=str(user.id), email=user.email, username=user.username)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )
