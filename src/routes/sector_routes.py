from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.dependencies.auth_dependencies import require_roles
from src.models.user import User
from src.schemas.sector_schema import SectorCreate, SectorUpdate, SectorResponse
from src.schemas.user_schema import UserRole
from src.services.sector_service import SectorService
from typing import List

sector_router = APIRouter()

@sector_router.post("/sectors")
async def create_sector(
    sector_data: SectorCreate,
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """Create new sector (Admin only)"""
    service = SectorService(db)
    result = await service.create_sector(sector_data, current_user.id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result

@sector_router.get("/sectors")
async def get_all_sectors(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """Get all sectors (Admin only)"""
    service = SectorService(db)
    result = await service.get_all_sectors(active_only)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result

@sector_router.get("/sectors/{sector_id}")
async def get_sector_by_id(
    sector_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get sector by ID (Admin only)"""
    service = SectorService(db)
    result = await service.get_sector_by_id(sector_id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result

@sector_router.put("/sectors/{sector_id}")
async def update_sector(
    sector_id: int,
    sector_data: SectorUpdate,
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """Update sector (Admin only)"""
    service = SectorService(db)
    result = await service.update_sector(sector_id, sector_data)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result

@sector_router.delete("/sectors/{sector_id}")
async def delete_sector(
    sector_id: int,
    hard_delete: bool = Query(True),
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """Delete sector (Admin only)"""
    service = SectorService(db)
    result = await service.delete_sector(sector_id, hard_delete)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result