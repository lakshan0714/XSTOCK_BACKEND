from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.models.user import User
from src.schemas.user_schema import UserCreate
from src.repository.user_repository import UserRepository
from fastapi import Cookie, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
import logging


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def signup_user(self, data: UserCreate):
        """Registers a new user in the system."""
        
        logging.info(f"Attempting to create user with email: {data}")
        existing_user = await self.user_repository.get_user_by_email(data.email)
        logging.debug(f"Existing user found: {existing_user}")

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        logging.debug("hashing password")
        hashed_pw = pwd_context.hash(data.password)
        logging.info(f"Password hashed for user: {data.email}")

        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_pw,
            role=data.role.value,
        )

        logging.info(f"role:{data.role.value}") 

        try:
            logging.debug("adding user to db")
            created_user = await self.user_repository.create_user(new_user)
            logging.info("user added")
            return {"message": "User created successfully", "user": created_user, "status_code": 200}
        
        except SQLAlchemyError as e:
            error_message = f"Database error: {str(e)}"
            return {"error": error_message, "status_code": 500}
        
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            return {"error": error_message, "status_code": 500}

    async def authenticate_user(self, email: str, password: str):
        """Authenticates a user by email and password.""" 
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not pwd_context.verify(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return user

    async def create_session(self, user_email: str):
        """Creates a new session for the user."""
        return await self.user_repository.create_session(user_email)

    async def validate_session(self, session_id: str):
        print(session_id)
        session = await self.user_repository.get_session_by_id(session_id)
        if session:
            user = await self.user_repository.get_user_by_email(session.user_mail)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")
        
        return session, user

    async def logout_user(self, session_id: str):
        """Logs out a user by deleting their session."""
        
        try:
            session = await self.user_repository.get_session_by_id(session_id)
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            await self.user_repository.delete_session(session)
            
            return {"msg": "User logged out successfully"}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Logout failed")

    async def get_current_user(self,session_id: str = Cookie(None), db: AsyncSession = Depends(get_db)):
        if not session_id:
            raise HTTPException(status_code=401, detail="Missing session ID")

        user_service = UserService(db)
        try:
            _, user = await user_service.validate_session(session_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to validate session")

    async def get_users(self):
        """Fetches all users from the database."""
        try:
            users = await self.user_repository.get_all_users()
            return users
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def get_user_by_id(self, user_id: int):
        """Fetches a user by their ID."""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


    async def update_user(self, user_id: int, update_data: dict):
        """Updates a user's information."""
        try:
            user_to_update = await self.user_repository.get_user_by_id(user_id)
            if not user_to_update:
                raise HTTPException(status_code=404, detail="User not found")

            await self._validate_email_update(user_to_update, update_data)
            await self._apply_updates(user_to_update, update_data)

            updated_user = await self.user_repository.update_user(user_to_update)

            return {"message": "User updated successfully", "user": updated_user, "status_code": 200}

        except HTTPException:
            await self.user_repository.rollback()
            raise
        except SQLAlchemyError as e:
            error_message = f"Database error: {str(e)}"
            return {"error": error_message, "status_code": 500}
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            return {"error": error_message, "status_code": 500}


    # ------------------ Helper Functions ------------------

    async def _validate_email_update(self, user_to_update, update_data):
        """Check if email is being updated and already exists"""
        if "email" in update_data and update_data["email"] != user_to_update.email:
            existing_user = await self.user_repository.get_user_by_email(update_data["email"])
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")


    async def _apply_updates(self, user_to_update, update_data):
        """Apply field updates to the user object"""
        for field, value in update_data.items():
            if hasattr(user_to_update, field):
                if field == "password":
                    hashed_pw = pwd_context.hash(value)
                    setattr(user_to_update, "password_hash", hashed_pw)
                elif field == "role":
                    setattr(user_to_update, field, value.value if hasattr(value, 'value') else value)
                else:
                    setattr(user_to_update, field, value)


    async def delete_user(self, user_id: int):
        """Deletes a user from the database."""
        try:
            user_to_delete = await self.user_repository.get_user_by_id(user_id)
            
            if not user_to_delete:
                raise HTTPException(status_code=404, detail="User not found")
            
            
        
            await self.user_repository.delete_user(user_to_delete)
            
            return {"message": "User deleted successfully", "status_code": 200}
            
        except HTTPException:
            await self.user_repository.rollback()
            raise
        except SQLAlchemyError as e:
            error_message = f"Database error: {str(e)}"
            return {"error": error_message, "status_code": 500}
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            return {"error": error_message, "status_code": 500}

    async def change_password(self, user_id: int, old_password: str, new_password: str, current_user: User):
        """Changes a user's password after verifying the old password."""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Check permissions
            if current_user.id != user.id :
                raise HTTPException(status_code=403, detail="Insufficient permissions to change this user's password")
            
            # Verify old password (only if user is changing their own password)
            if current_user.id == user.id:
                if not pwd_context.verify(old_password, user.password_hash):
                    raise HTTPException(status_code=400, detail="Invalid current password")
            
            # Hash and set new password
            new_hashed_pw = pwd_context.hash(new_password)
            user.password_hash = new_hashed_pw
            
            updated_user = await self.user_repository.update_user(user)
            
            return {"message": "Password changed successfully", "status_code": 200}
            
        except HTTPException:
            await self.user_repository.rollback()
            raise
        except SQLAlchemyError as e:
            error_message = f"Database error: {str(e)}"
            return {"error": error_message, "status_code": 500}
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            return {"error": error_message, "status_code": 500}
