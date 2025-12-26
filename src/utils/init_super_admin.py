from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import Settings
from src.models.user import User
import logging

settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_super_admin(db:Session):
    existing_user=db.query(User).filter(User.email==settings.SUPER_ADMIN_EMAIL).first()
    if not existing_user:
        hashed_password = pwd_context.hash(settings.SUPER_ADMIN_PASSWORD)
        super_admin = User(
            username="SuperAdmin",
            email=settings.SUPER_ADMIN_EMAIL,
            password_hash=hashed_password,
            role="superadmin"  # Assuming 'superadmin' is a valid UserRole
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        logging.info("Super admin created successfully.")
        

