"""
Authentication dependencies for FastAPI endpoints.
Handles token extraction, verification, and role-based access control.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_local_db
from app.models.user import User, UserRole
from app.utils.security import decode_token
from app.schemas.auth import TokenData

# OAuth2 scheme for token extraction
# tokenUrl is the endpoint where clients get tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================================================
# CREDENTIALS EXCEPTION
# ============================================================================

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_local_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Decode token to get username
    username = decode_token(token)
    
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    return user


from app.core.license import license_service

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_local_db)
) -> User:
    """
    Ensure current user is active.
    Also checks for license expiration (unless user is Super Admin).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: 400 if user is inactive
        HTTPException: 403 if license is expired (and not Super Admin)
    """
    print(f"[DEBUG] get_current_active_user: Verifying user {current_user.username}")
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # Check license status
    # Super Admin can bypass expired license to fix it
    if current_user.role != UserRole.SUPER_ADMIN:
        print("[DEBUG] get_current_active_user: Checking license...")
        license_status = license_service.get_license_status(db)
        print(f"[DEBUG] get_current_active_user: License status: {license_status.get('status')}")
        if license_status["status"] == "expired":
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=license_status["message"]
            )
            
    print("[DEBUG] get_current_active_user: Verification complete.")
    return current_user


# ============================================================================
# AUTHORIZATION DEPENDENCIES (ROLE-BASED)
# ============================================================================

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Ensure current user has admin role (or super admin).
    Used to protect admin-only endpoints.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: Current admin user
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin privileges required"
        )
    return current_user


async def get_pharmacist_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Ensure current user has pharmacist or admin role.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: Current pharmacist or admin user
        
    Raises:
        HTTPException: 403 if user is neither pharmacist nor admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.PHARMACIST, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Pharmacist or Admin privileges required"
        )
    return current_user


async def get_super_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Ensure current user has super admin role.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: Current super admin user
        
    Raises:
        HTTPException: 403 if user is not super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Super Admin privileges required"
        )
    return current_user
