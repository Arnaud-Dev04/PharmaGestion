"""
Authentication routes: login, register, get user info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_local_db
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserCreate, UserResponse, UserLogin
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.auth.dependencies import get_current_active_user, get_admin_user

# Create router
router = APIRouter()


# ============================================================================
# AUTHENTICATION HELPER
# ============================================================================

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Authenticate user by username and password.
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
        
    Returns:
        User if authenticated, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

@router.post("/login", response_model=Token, summary="Login to get access token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_local_db)
):
    """
    Login endpoint - Authenticate user and return JWT token.
    
    **OAuth2 compatible** - accepts form data with username and password.
    
    Returns:
        Token: JWT access token with type "bearer"
        
    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 400: If user is inactive
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================================
# REGISTER ENDPOINT (Admin Only)
# ============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register new user (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_local_db),
    current_admin: User = Depends(get_admin_user)
):
    """
    Register a new user - **Admin only**.
    
    Creates a new user account with hashed password.
    
    Args:
        user_data: User creation data (username, password, role)
        
    Returns:
        UserResponse: Created user data (without password)
        
    Raises:
        HTTPException 400: If username already exists
        HTTPException 403: If current user is not admin
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ============================================================================
# GET CURRENT USER INFO
# ============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information"
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException 401: If not authenticated
    """
    print(f"[DEBUG] /auth/me endpoint reached for {current_user.username}")
    return current_user


# ============================================================================
# USER MANAGEMENT (Admin Only)
# ============================================================================

from typing import List
from app.schemas.auth import UserUpdatePassword

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all users (Admin only)",
)
async def get_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """List all registered users."""
    query = db.query(User)
    
    # Hide super admins from regular admins
    if current_user.role != UserRole.SUPER_ADMIN:
        query = query.filter(User.role != UserRole.SUPER_ADMIN)
        
    users = query.all()
    return users


@router.put(
    "/users/{user_id}/password",
    summary="Change user password (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def change_user_password(
    user_id: int,
    password_data: UserUpdatePassword,
    db: Session = Depends(get_local_db)
):
    """Change user password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    user.password_hash = hash_password(password_data.password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.delete(
    "/users/{user_id}",
    summary="Delete a user (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """Delete a user account."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has sales relations preventing deletion?
    # For now, let's assume we keep sales history even if user deleted (or set null).
    # But usually sales.user_id is FK. We might need Soft Delete or check usage.
    # To be safe, we might just set is_active=False instead of DELETE.
    # But user asked for delete. Let's try Delete, if it fails due to FK, we catch it.
    
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        # Fallback to soft delete if FK constraint fails
        user.is_active = False
        db.commit()
        return {"message": "User deactivated (could not delete due to existing records)"}
        
    return {"message": "User deleted successfully"}


@router.put(
    "/users/{user_id}/toggle-status",
    response_model=UserResponse,
    summary="Toggle user active status (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def toggle_user_status(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_local_db)
):
    """
    Toggle a user's active status (activate or deactivate).
    Useful for suspending users during leave or for disciplinary reasons.
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own admin account"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Toggle status
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return user


# ============================================================================
# USER SALES STATISTICS
# ============================================================================

from app.schemas.user_stats import UserSalesStats, UserPerformance, TopProductSold
from app.models.sales import Sale, SaleItem
from app.models.medicine import Medicine
from sqlalchemy import func, desc
from typing import Optional as TypingOptional
from datetime import datetime, timedelta


@router.get(
    "/users/{user_id}/sales-stats",
    response_model=UserSalesStats,
    summary="Get user sales statistics (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def get_user_sales_stats(
    user_id: int,
    start_date: TypingOptional[str] = None,
    end_date: TypingOptional[str] = None,
    db: Session = Depends(get_local_db)
):
    """
    Get detailed sales statistics for a specific user.
    
    Query Parameters:
        - start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
        - end_date: End date (YYYY-MM-DD), defaults to today
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Parse dates
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = datetime.now()
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_dt = end_dt - timedelta(days=30)
    
    # Get sales for this user
    sales_query = db.query(Sale).filter(
        Sale.user_id == user_id,
        Sale.date >= start_dt,
        Sale.date <= end_dt
    )
    
    sales = sales_query.all()
    total_sales = len(sales)
    total_revenue = sum(sale.total_amount for sale in sales)
    average_sale = total_revenue / total_sales if total_sales > 0 else 0
    
    # Count unique customers
    customers_served = db.query(func.count(func.distinct(Sale.customer_id))).filter(
        Sale.user_id == user_id,
        Sale.date >= start_dt,
        Sale.date <= end_dt,
        Sale.customer_id.isnot(None)
    ).scalar() or 0
    
    # Top products sold
    top_products_query = db.query(
        Medicine.id,
        Medicine.name,
        Medicine.code,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.total_price).label('total_revenue')
    ).join(
        SaleItem, SaleItem.medicine_id == Medicine.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.user_id == user_id,
        Sale.date >= start_dt,
        Sale.date <= end_dt
    ).group_by(
        Medicine.id, Medicine.name, Medicine.code
    ).order_by(
        desc('total_quantity')
    ).limit(10)
    
    top_products = []
    for prod in top_products_query.all():
        top_products.append(TopProductSold(
            medicine_id=prod.id,
            medicine_name=prod.name,
            medicine_code=prod.code,
            quantity_sold=prod.total_quantity,
            revenue_generated=prod.total_revenue
        ))
    
    # Sales by date for chart
    sales_by_date_query = db.query(
        func.date(Sale.date).label('sale_date'),
        func.count(Sale.id).label('count'),
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        Sale.user_id == user_id,
        Sale.date >= start_dt,
        Sale.date <= end_dt
    ).group_by(
        func.date(Sale.date)
    ).order_by('sale_date')
    
    sales_by_date = []
    for row in sales_by_date_query.all():
        sales_by_date.append({
            'date': row.sale_date.isoformat() if row.sale_date else None,
            'count': row.count,
            'revenue': row.revenue
        })
    
    return UserSalesStats(
        user_id=user.id,
        username=user.username,
        total_sales=total_sales,
        total_revenue=total_revenue,
        average_sale_amount=average_sale,
        customers_served=customers_served,
        top_products=top_products,
        sales_by_date=sales_by_date
    )


@router.get(
    "/users/sales-performance",
    response_model=List[UserPerformance],
    summary="Get all users sales performance comparison (Admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def get_users_performance(
    start_date: TypingOptional[str] = None,
    end_date: TypingOptional[str] = None,
    db: Session = Depends(get_local_db)
):
    """
    Get sales performance comparison for all users.
    Ranked by total revenue.
    
    Query Parameters:
        - start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
        - end_date: End date (YYYY-MM-DD), defaults to today
    """
    # Parse dates
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = datetime.now()
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_dt = end_dt - timedelta(days=30)
    
    # Get all users
    users = db.query(User).all()
    
    performances = []
    for user in users:
        # Get sales stats for this user
        sales = db.query(Sale).filter(
            Sale.user_id == user.id,
            Sale.date >= start_dt,
            Sale.date <= end_dt
        ).all()
        
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        average_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        performances.append(UserPerformance(
            user_id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            total_sales=total_sales,
            total_revenue=total_revenue,
            average_sale_amount=average_sale
        ))
    
    # Sort by revenue and assign ranks
    performances.sort(key=lambda x: x.total_revenue, reverse=True)
    for idx, perf in enumerate(performances, start=1):
        perf.rank = idx
    
    return performances

