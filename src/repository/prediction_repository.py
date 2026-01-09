from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from src.models.prediction import Prediction
from typing import List, Optional
from datetime import datetime, timedelta

class PredictionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_prediction(self, prediction_data: dict) -> Prediction:
        """Save prediction to database"""
        prediction = Prediction(**prediction_data)
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction
    
    async def get_prediction_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get single prediction"""
        result = await self.db.execute(
            select(Prediction).where(Prediction.id == prediction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_predictions(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Prediction]:
        """Get user's prediction history"""
        result = await self.db.execute(
            select(Prediction)
            .where(Prediction.user_id == user_id)
            .order_by(desc(Prediction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_prediction_count(self, user_id: int) -> int:
        """Get total prediction count for user"""
        result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.user_id == user_id)
        )
        return result.scalar()
    
    async def get_all_predictions(self, skip: int = 0, limit: int = 100) -> List[Prediction]:
        """Get all predictions (admin)"""
        result = await self.db.execute(
            select(Prediction)
            .order_by(desc(Prediction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    # ==================== ANALYTICS FUNCTIONS (FOR ADMIN DASHBOARD) ====================
    
    async def get_prediction_stats(self) -> dict:
        """Get overall prediction statistics"""
        
        # Total predictions
        total_result = await self.db.execute(
            select(func.count(Prediction.id))
        )
        total = total_result.scalar()
        
        # BUY count
        buy_result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.final_recommendation == "BUY")
        )
        buy_count = buy_result.scalar()
        
        # SELL count
        sell_result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.final_recommendation == "SELL")
        )
        sell_count = sell_result.scalar()
        
        # HOLD count
        hold_result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.final_recommendation == "HOLD")
        )
        hold_count = hold_result.scalar()
        
        # Average confidence
        avg_conf_result = await self.db.execute(
            select(func.avg(Prediction.final_confidence))
        )
        avg_confidence = avg_conf_result.scalar() or 0.0
        
        return {
            "total_predictions": total,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "hold_count": hold_count,
            "buy_percentage": round((buy_count / total * 100) if total > 0 else 0, 2),
            "sell_percentage": round((sell_count / total * 100) if total > 0 else 0, 2),
            "hold_percentage": round((hold_count / total * 100) if total > 0 else 0, 2),
            "average_confidence": round(avg_confidence, 2)
        }
    
    async def get_predictions_by_sector(self) -> List[dict]:
        """Get prediction breakdown by sector"""
        from sqlalchemy import case
        
        result = await self.db.execute(
            select(
                Prediction.sector,
                func.count(Prediction.id).label('total'),
                func.sum(case((Prediction.final_recommendation == "BUY", 1), else_=0)).label('buy'),
                func.sum(case((Prediction.final_recommendation == "SELL", 1), else_=0)).label('sell'),
                func.sum(case((Prediction.final_recommendation == "HOLD", 1), else_=0)).label('hold'),
                func.avg(Prediction.final_confidence).label('avg_confidence')
            )
            .group_by(Prediction.sector)
        )
        
        return [
            {
                "sector": row[0] or "Unknown",
                "total": row[1],
                "buy": row[2],
                "sell": row[3],
                "hold": row[4],
                "avg_confidence": round(row[5], 2) if row[5] else 0.0
            }
            for row in result.all()
        ]
    

    async def get_top_predicted_stocks(self, limit: int = 10) -> List[dict]:
        """Get most frequently predicted stocks"""
        result = await self.db.execute(
            select(
                Prediction.ticker,
                Prediction.company_name,
                func.count(Prediction.id).label('prediction_count')
            )
            .group_by(Prediction.ticker, Prediction.company_name)
            .order_by(desc('prediction_count'))
            .limit(limit)
        )
        
        stocks_list = []
        for row in result.all():
            ticker = row[0]
            company_name = row[1]
            prediction_count = row[2]
            
            # Get most common recommendation for this stock
            rec_result = await self.db.execute(
                select(
                    Prediction.final_recommendation,
                    func.count(Prediction.id).label('count')
                )
                .where(Prediction.ticker == ticker)
                .group_by(Prediction.final_recommendation)
                .order_by(desc('count'))
                .limit(1)
            )
            
            rec_row = rec_result.first()
            most_common = rec_row[0] if rec_row else "N/A"
            most_common_count = rec_row[1] if rec_row else 0
            
            stocks_list.append({
                "ticker": ticker,
                "company_name": company_name,
                "prediction_count": prediction_count,
                "most_common_prediction": most_common,
                "most_common_count": most_common_count
            })
        
        return stocks_list
    
    async def get_predictions_today(self) -> int:
        """Get count of predictions made today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.created_at >= today_start)
        )
        return result.scalar()
    
    async def get_predictions_this_week(self) -> int:
        """Get count of predictions made this week"""
        week_start = datetime.now() - timedelta(days=7)
        result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.created_at >= week_start)
        )
        return result.scalar()
    
    async def get_predictions_this_month(self) -> int:
        """Get count of predictions made this month"""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.count(Prediction.id))
            .where(Prediction.created_at >= month_start)
        )
        return result.scalar()