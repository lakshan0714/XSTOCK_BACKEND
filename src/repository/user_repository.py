from datetime import datetime, timezone, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.models.user import User, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete
import logging


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str):
        """Get user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, user: User):
        """Create a new user in the database."""
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            await self.db.rollback()
            raise e

    async def create_session(self, user_email: str):
        """Create a new session for the user."""
        session_id = str(uuid.uuid4())
        new_session = Session(
            user_mail=user_email,
            session_id=session_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session

    async def get_session_by_id(self, session_id: str):
        """Get session by session ID."""
        result = await self.db.execute(select(Session).where(Session.session_id == session_id))
        return result.scalar_one_or_none()

    async def delete_session(self, session: Session):
        """Delete a session from the database."""
        await self.db.delete(session)
        await self.db.commit()


    async def get_all_users(self):
        """Get all users from the database."""
        result = await self.db.execute(select(User).order_by(User.id.asc()))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int):
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user(self, user: User):
        """Update user in the database."""
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            await self.db.rollback()
            raise e

    async def delete_user(self, user: User):
        """Delete user from the database."""
        try:
            # Delete all sessions associated with this user first
            await self.db.execute(delete(Session).where(Session.user_mail == user.email))
            # Delete the user
            await self.db.delete(user)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            await self.db.rollback()
            raise e

    async def rollback(self):
        """Rollback the current transaction."""
        await self.db.rollback()
