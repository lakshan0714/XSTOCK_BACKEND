from fastapi import HTTPException,status
from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.dependencies.auth_dependencies import require_roles
from src.models.user import User
from src.schemas.user_schema import UserCreate, UserRole, Userlogin, UserUpdate, PasswordChange, AdminPasswordChange
from src.services.user_service import UserService
from src.config.settings import Settings


user_router = APIRouter()
settings = Settings()


IS_PROD = settings.ENV == "prod"
COOKIE_DOMAIN = settings.COOKIE_DOMAIN 


@user_router.post("/signup")
async def signup_route(data: UserCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(require_roles(UserRole.superadmin))):
    """
    Create a new user account.
    Only SuperAdmin Create Account.
   
    Args:
        data: User creation data
        db: Database session
       
    Returns:
        JSON response with user data or error
       
    Raises:
        HTTPException: If user creation fails
    """
       
    user_object = UserService(db)
    try:
        response = await user_object.signup_user(data)
        if response.get("status_code") == 200:
            return response
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Service error creating product: {str(e)}")     

        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@user_router.post("/login")
async def login_route(data: Userlogin, response: Response, db: AsyncSession = Depends(get_db)):
    """User login endpoint."""
    user_object = UserService(db)
    user = await user_object.authenticate_user(data.email, data.password)
   
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
   
    try:
        # Creating a session
        session = await user_object.create_session(data.email)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
   
    response.set_cookie(
        key="session_id",
        value=session.session_id,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="none" if IS_PROD else "lax",
        domain=COOKIE_DOMAIN if IS_PROD else None,
        expires=session.expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )


    return {"message": "Login successful", "data": user}


@user_router.get("/me")
async def get_me(current_user: User = Depends(require_roles([UserRole.superadmin,UserRole.admin]))):
    """Get current user profile."""
    return {"data": current_user}



@user_router.post("/logout")
async def logout_route(response: Response, session_id: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    """User logout endpoint."""
    if session_id:
        user_object = UserService(db)
        await user_object.logout_user(session_id)
        response.delete_cookie("session_id")
        return {"message": "Logout successful"}
    else:
        raise HTTPException(status_code=400, detail="No session found")


@user_router.get("/users")
async def get_users_route(current_user: User = Depends(require_roles(UserRole.superadmin)), db: AsyncSession = Depends(get_db)):
    """Get all users (superadmin only or for user management)."""
    user_object = UserService(db)
    try:
        # Fetch all users
        users = await user_object.get_users()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
       
        return {"data": users}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



@user_router.get("/users/{user_id}")
async def get_user_by_id_route(
    user_id: int, 
    current_user: User = Depends(require_roles(UserRole.superadmin)), 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID."""
    user_object = UserService(db)
    try:
        user = await user_object.get_user_by_id(user_id)
        
        return {"data": user}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



@user_router.put("/users/{user_id}")
async def update_user_route(
    user_id: int,
    update_data: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.superadmin)),
    db: AsyncSession = Depends(get_db)
):
    """Update a user's information."""
    user_object = UserService(db)
    
    # Convert Pydantic model to dict, excluding None values
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    try:
        response = await user_object.update_user(user_id, update_dict)
        if response.get("status_code") == 200:
            return response
        else:
            raise HTTPException(
                status_code=response.get("status_code", 500), 
                detail=response.get("error", "An error occurred")
            )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)




@user_router.delete("/users/{user_id}")
async def delete_user_route(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.superadmin)),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user account."""
    user_object = UserService(db)
    
    try:
        response = await user_object.delete_user(user_id)
        if response.get("status_code") == 200:
            return response
        else:
            raise HTTPException(
                status_code=response.get("status_code", 500), 
                detail=response.get("error", "An error occurred")
            )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



@user_router.put("/users/{user_id}/password")
async def change_password_route(
    user_id: int,
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.superadmin))
):
    """Change a user's password."""
    user_object = UserService(db)
    
    try:
        response = await user_object.change_password(
            user_id, 
            password_data.old_password, 
            password_data.new_password, 
            current_user
        )
        if response.get("status_code") == 200:
            return response
        else:
            raise HTTPException(
                status_code=response.get("status_code", 500), 
                detail=response.get("error", "An error occurred")
            )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)



@user_router.put("/admin/users/{user_id}/password")
async def admin_change_password_route(
    user_id: int,
    password_data: AdminPasswordChange,
   
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.superadmin)),
):
    """Admin endpoint to change any user's password without requiring old password."""
    # Check if current user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user_object = UserService(db)
    
    try:
        response = await user_object.change_password(
            user_id, 
            "", # Empty old password for admin
            password_data.new_password, 
            current_user
        )
        if response.get("status_code") == 200:
            return response
        else:
            raise HTTPException(
                status_code=response.get("status_code", 500), 
                detail=response.get("error", "An error occurred")
            )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
