from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.prediction_repository import PredictionRepository
from datetime import datetime, timedelta
  # Get counts from other services
from src.repository.user_repository import UserRepository
from src.repository.stock_repository import StockRepository
from src.repository.sector_repository import SectorRepository

# Count users, stocks, sectors
from sqlalchemy import select, func
from src.models.user import User
from src.models.stock import Stock
from src.models.sector import Sector

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository = PredictionRepository(db)
    
    async def get_dashboard_stats(self) -> dict:
        """Get comprehensive dashboard statistics"""
        try:
            # Overall stats
            overall_stats = await self.repository.get_prediction_stats()
            
            # Time-based counts
            today_count = await self.repository.get_predictions_today()
            week_count = await self.repository.get_predictions_this_week()
            month_count = await self.repository.get_predictions_this_month()
            
            
            user_repo = UserRepository(self.repository.db)
            stock_repo = StockRepository(self.repository.db)
            sector_repo = SectorRepository(self.repository.db)
            
            
            users_count = await self.repository.db.execute(select(func.count(User.id)))
            total_users = users_count.scalar() or 0
            
            stocks_count = await self.repository.db.execute(select(func.count(Stock.id)))
            total_stocks = stocks_count.scalar() or 0
            
            sectors_count = await self.repository.db.execute(select(func.count(Sector.id)))
            total_sectors = sectors_count.scalar() or 0
            
            # Sector breakdown
            sector_stats = await self.repository.get_predictions_by_sector()
            
            # Top stocks
            top_stocks = await self.repository.get_top_predicted_stocks(10)
            
            return {
                "status_code": 200,
                "data": {
                    "overview": {
                        **overall_stats,
                        "total_users": total_users,
                        "total_stocks": total_stocks,
                        "total_sectors": total_sectors,
                        "predictions_today": today_count,
                        "predictions_this_week": week_count,
                        "predictions_this_month": month_count
                    },
                    "sector_breakdown": sector_stats,
                    "top_predicted_stocks": top_stocks
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status_code": 500,
                "error": f"Error fetching analytics: {str(e)}"
            }
    
    async def get_sector_analytics(self) -> dict:
        """Get detailed sector-wise analytics"""
        try:
            sector_stats = await self.repository.get_predictions_by_sector()
            
            return {
                "status_code": 200,
                "data": sector_stats
            }
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching sector analytics: {str(e)}"
            }
    
    async def get_top_stocks(self, limit: int = 20) -> dict:
        """Get top predicted stocks"""
        try:
            top_stocks = await self.repository.get_top_predicted_stocks(limit)
            
            return {
                "status_code": 200,
                "data": top_stocks
            }
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching top stocks: {str(e)}"
            }
    
    async def get_all_predictions(self, skip: int = 0, limit: int = 100) -> dict:
        """Get all predictions with pagination (Admin only)"""
        try:
            predictions = await self.repository.get_all_predictions(skip, limit)
            
            # Get total count
            stats = await self.repository.get_prediction_stats()
            total = stats['total_predictions']
            
            # Convert to dicts
            predictions_data = []
            for pred in predictions:
                predictions_data.append({
                    "id": pred.id,
                    "user_id": pred.user_id,
                    "ticker": pred.ticker,
                    "company_name": pred.company_name,
                    "sector": pred.sector,
                    "final_recommendation": pred.final_recommendation,
                    "final_confidence": pred.final_confidence,
                    "predicted_at": pred.created_at.isoformat() if pred.created_at else None
                })
            
            return {
                "status_code": 200,
                "data": predictions_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status_code": 500,
                "error": f"Error fetching predictions: {str(e)}"
            }