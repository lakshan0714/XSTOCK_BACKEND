# auth_dependencies.py
from typing import List, Union, Callable
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.services.user_service import UserService
from src.models.user import User
from src.schemas.user_schema import UserRole  

async def get_current_user(session_id: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    """Dependency to get current authenticated user."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session ID")
    
    user_service = UserService(db)
    try:
        _, user = await user_service.validate_session(session_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")



def require_roles(allowed_roles: Union[UserRole, List[UserRole]]) -> Callable:
    """
    Create a dependency that requires specific roles.
    
    Args:
        allowed_roles: Single UserRole enum or list of allowed UserRole enums
        
    Returns:
        FastAPI dependency function
    """
    # Normalize to list
    if isinstance(allowed_roles, UserRole):
        allowed_roles = [allowed_roles]
    
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Check if current user has required role(s)"""
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role"
            )
        
        # Convert string role to enum for comparison
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
        
        if user_role not in allowed_roles:
            role_names = [role.value for role in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(role_names)}"
            )
        
        return current_user
    
    return role_checker
