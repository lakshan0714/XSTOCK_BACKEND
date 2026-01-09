from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.dependencies.auth_dependencies import require_roles
from src.models.user import User
from src.schemas.stock_schema import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockDetailResponse,
    DashboardStats
)
from src.schemas.user_schema import UserRole
from src.services.stock_service import StockService
from typing import List, Optional

stock_router = APIRouter()

@stock_router.post("/stocks", response_model=dict)
async def create_stock(
    stock_data: StockCreate,
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new stock (Admin only)
    Automatically calculates all ratios
    """
    service = StockService(db)
    result = await service.create_stock(stock_data, current_user.id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.get("/stocks", response_model=dict)
async def get_all_stocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    sector_id: int = Query(None),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all stocks with pagination (Admin only)
    """
    service = StockService(db)
    result = await service.get_all_stocks(skip, limit, active_only,sector_id=sector_id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.get("/stocks/{stock_id}", response_model=dict)
async def get_stock_by_id(
    stock_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get stock by ID with calculated ratios (Admin only)
    """
    service = StockService(db)
    result = await service.get_stock_by_id(stock_id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.get("/stocks/ticker/{ticker}", response_model=dict)
async def get_stock_by_ticker(
    ticker: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get stock by ticker symbol (Admin only)
    """
    service = StockService(db)
    result = await service.get_stock_by_ticker(ticker)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.put("/stocks/{stock_id}", response_model=dict)
async def update_stock(
    stock_id: int,
    stock_data: StockUpdate,
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update stock (Admin only)
    Automatically recalculates all ratios
    """
    service = StockService(db)
    result = await service.update_stock(stock_id, stock_data)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.delete("/stocks/{stock_id}", response_model=dict)
async def delete_stock(
    stock_id: int,
    hard_delete: bool = Query(False, description="Permanently delete stock"),
    current_user: User = Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete stock (Admin only)
    Soft delete by default, use hard_delete=true for permanent deletion
    """
    service = StockService(db)
    result = await service.delete_stock(stock_id, hard_delete)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result


@stock_router.get("/dashboard/stats", response_model=dict)
async def get_dashboard_stats(
    current_user: User =Depends(require_roles(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics (Admin only)
    - Total stocks
    - Active/Inactive counts
    - Sector distribution
    - Recent activities
    """
    service = StockService(db)
    result = await service.get_dashboard_stats()
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "An error occurred")
        )
    
    return result