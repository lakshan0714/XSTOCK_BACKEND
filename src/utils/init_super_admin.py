from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import Settings
from src.models.user import User
import logging

settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin(db:Session):
    existing_user=db.query(User).filter(User.email==settings.ADMIN_EMAIL).first()
    if not existing_user:
        hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
        admin = User(
            username="Admin",
            email=settings.ADMIN_EMAIL,
            password_hash=hashed_password,
            role="admin"  # Assuming 'admin' is a valid UserRole
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logging.info(" admin created successfully.")
        

