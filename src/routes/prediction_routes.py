from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.dependencies.auth_dependencies import require_roles
from src.models.user import User
from src.schemas.prediction_schema import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistoryItem,
    PredictionDetailResponse,
    PredictionStats,
    SectorPredictionStats,
    TopPredictedStock
)
from src.schemas.user_schema import UserRole
from src.services.prediction_service import PredictionService
from src.services.analytics_service import AnalyticsService
from src.services.model_loader import model_loader
from typing import List

prediction_router = APIRouter()

# ==================== HEALTH CHECK ====================

@prediction_router.get("/health")
async def health_check():
    """Check if ML models are loaded and ready"""
    is_healthy = model_loader.health_check()
    
    if is_healthy:
        return {
            "status": "healthy",
            "message": "All ML models loaded successfully",
            "models_loaded": {
                "model_1_valuation": True,
                "model_2_health": True,
                "model_3_growth": True
            }
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="ML models not loaded. Please restart the server."
        )

# ==================== USER ENDPOINTS ====================

@prediction_router.post("/stock", response_model=dict)
async def predict_stock(
    request: PredictionRequest,
    current_user: User = Depends(require_roles([UserRole.user, UserRole.admin])),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict stock recommendation (BUY/SELL/HOLD)
    
    Returns:
    - Model 1 (Valuation): UNDERVALUED/FAIR/OVERVALUED + explanation
    - Model 2 (Health): EXCELLENT/FAIR/POOR + explanation
    - Model 3 (Growth): STRONG_GROWTH/MODERATE_GROWTH/WEAK_GROWTH/DECLINING + explanation
    - Ensemble: Final BUY/SELL/HOLD recommendation
    """
    service = PredictionService(db)
    result = await service.predict_stock(request.ticker, current_user.id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Prediction failed")
        )
    
    return result


@prediction_router.get("/history", response_model=dict)
async def get_prediction_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.user, UserRole.admin])),
    db: AsyncSession = Depends(get_db)
):
    """Get user's prediction history"""
    service = PredictionService(db)
    result = await service.get_user_predictions(current_user.id, skip, limit)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch history")
        )
    
    return result


@prediction_router.get("/history/{prediction_id}", response_model=dict)
async def get_prediction_detail(
    prediction_id: int,
    current_user: User = Depends(require_roles([UserRole.user, UserRole.admin])),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed prediction information"""
    service = PredictionService(db)
    result = await service.get_prediction_by_id(prediction_id, current_user.id)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch prediction")
        )
    
    return result

# ==================== ADMIN ENDPOINTS ====================

@prediction_router.get("/admin/stats", response_model=dict)
async def get_admin_statistics(
    current_user: User = Depends(require_roles([UserRole.admin, UserRole.user])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive prediction analytics (Admin only)
    
    Returns:
    - Overall statistics (total, BUY/SELL/HOLD counts, percentages)
    - Time-based counts (today, this week, this month)
    - Sector breakdown
    - Top predicted stocks
    """
    service = AnalyticsService(db)
    result = await service.get_dashboard_stats()
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch statistics")
        )
    
    return result


@prediction_router.get("/admin/by-sector", response_model=dict)
async def get_sector_analytics(
    current_user: User = Depends(require_roles([UserRole.admin, UserRole.user])),
    db: AsyncSession = Depends(get_db)
):
    """Get prediction breakdown by sector (Admin only)"""
    service = AnalyticsService(db)
    result = await service.get_sector_analytics()
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch sector analytics")
        )
    
    return result


@prediction_router.get("/admin/top-stocks", response_model=dict)
async def get_top_stocks(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.admin, UserRole.user])),
    db: AsyncSession = Depends(get_db)
):
    """Get most frequently predicted stocks (Admin only)"""
    service = AnalyticsService(db)
    result = await service.get_top_stocks(limit)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch top stocks")
        )
    
    return result


@prediction_router.get("/admin/all", response_model=dict)
async def get_all_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_roles([UserRole.admin, UserRole.user])),
    db: AsyncSession = Depends(get_db)
):
    """Get all predictions with pagination (Admin only)"""
    service = AnalyticsService(db)
    result = await service.get_all_predictions(skip, limit)
    
    if result.get("status_code") != 200:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result.get("error", "Failed to fetch predictions")
        )
    
    return result