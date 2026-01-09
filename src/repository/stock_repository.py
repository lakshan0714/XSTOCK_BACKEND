from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload, joinedload
from src.models.stock import Stock
from src.models.stock_ratios import StockRatio
from src.models.sector import Sector
from typing import List, Optional

class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_stock(self, stock_data: dict) -> Stock:
        """Create a new stock"""
        stock = Stock(**stock_data)
        self.db.add(stock)
        await self.db.commit()
        await self.db.refresh(stock)
        return stock

    async def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID with sector"""
        result = await self.db.execute(
            select(Stock)
            .options(joinedload(Stock.sector))
            .where(Stock.id == stock_id)
        )
        return result.scalar_one_or_none()

    async def get_stock_by_ticker(self, ticker: str) -> Optional[Stock]:
        """Get stock by ticker with sector"""
        result = await self.db.execute(
            select(Stock)
            .options(joinedload(Stock.sector))
            .where(Stock.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()

    async def get_all_stocks(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = False,
        sector_id: Optional[int] = None
    ) -> List[Stock]:
        """Get all stocks with pagination and filters"""
        query = select(Stock).options(joinedload(Stock.sector))
        
        if active_only:
            query = query.where(Stock.is_active == True)
        
        if sector_id:
            query = query.where(Stock.sector_id == sector_id)
        
        query = query.offset(skip).limit(limit).order_by(desc(Stock.created_at))
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_stock(self, stock_id: int, update_data: dict) -> Optional[Stock]:
        """Update stock"""
        stock = await self.get_stock_by_id(stock_id)
        if not stock:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(stock, key):
                setattr(stock, key, value)
        
        await self.db.commit()
        await self.db.refresh(stock)
        return stock

    async def delete_stock(self, stock_id: int) -> bool:
        """Soft delete stock"""
        stock = await self.get_stock_by_id(stock_id)
        if not stock:
            return False
        
        stock.is_active = False
        await self.db.commit()
        return True

    async def hard_delete_stock(self, stock_id: int) -> bool:
        """Hard delete stock (also deletes ratios due to CASCADE)"""
        stock = await self.get_stock_by_id(stock_id)
        if not stock:
            return False
        
        await self.db.delete(stock)
        await self.db.commit()
        return True

    async def get_total_stocks(self, active_only: bool = False) -> int:
        """Get total stock count"""
        query = select(func.count(Stock.id))
        
        if active_only:
            query = query.where(Stock.is_active == True)
        
        result = await self.db.execute(query)
        return result.scalar()

    async def get_active_stocks_count(self) -> int:
        """Get active stock count"""
        result = await self.db.execute(
            select(func.count(Stock.id)).where(Stock.is_active == True)
        )
        return result.scalar()

    async def get_sector_distribution(self) -> List[dict]:
        """Get stock distribution by sector"""
        result = await self.db.execute(
            select(Sector.name, func.count(Stock.id).label('count'))
            .join(Stock, Stock.sector_id == Sector.id)
            .where(Stock.is_active == True)
            .group_by(Sector.name)
        )
        return [{"sector": row[0], "count": row[1]} for row in result.all()]

    async def get_recent_stocks(self, limit: int = 10) -> List[Stock]:
        """Get recently added stocks"""
        result = await self.db.execute(
            select(Stock)
            .options(joinedload(Stock.sector))
            .where(Stock.is_active == True)
            .order_by(desc(Stock.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    # ==================== STOCK RATIOS METHODS ====================
    
    async def create_stock_ratios(self, ratio_data: dict) -> StockRatio:
        """Create calculated ratios"""
        ratio = StockRatio(**ratio_data)
        self.db.add(ratio)
        await self.db.commit()
        await self.db.refresh(ratio)
        return ratio

    async def get_stock_ratios(self, stock_id: int) -> Optional[StockRatio]:
        """Get ratios for a stock"""
        result = await self.db.execute(
            select(StockRatio).where(StockRatio.stock_id == stock_id)
        )
        return result.scalar_one_or_none()

    async def update_stock_ratios(self, stock_id: int, ratio_data: dict) -> Optional[StockRatio]:
        """Update or create stock ratios"""
        ratio = await self.get_stock_ratios(stock_id)
        
        if ratio:
            # Update existing
            for key, value in ratio_data.items():
                if hasattr(ratio, key):
                    setattr(ratio, key, value)
        else:
            # Create new
            ratio = StockRatio(stock_id=stock_id, **ratio_data)
            self.db.add(ratio)
        
        await self.db.commit()
        await self.db.refresh(ratio)
        return ratio

    async def delete_stock_ratios(self, stock_id: int) -> bool:
        """Delete stock ratios"""
        ratio = await self.get_stock_ratios(stock_id)
        if not ratio:
            return False
        
        await self.db.delete(ratio)
        await self.db.commit()
        return True

    async def get_stock_with_ratios(self, stock_id: int) -> Optional[dict]:
        """Get stock with its calculated ratios"""
        stock = await self.get_stock_by_id(stock_id)
        if not stock:
            return None
        
        ratios = await self.get_stock_ratios(stock_id)
        
        return {
            "stock": stock,
            "ratios": ratios
        }

    async def search_stocks(self, query: str, limit: int = 20) -> List[Stock]:
        """Search stocks by ticker or company name"""
        search_query = select(Stock).options(joinedload(Stock.sector))
        
        search_pattern = f"%{query}%"
        search_query = search_query.where(
            and_(
                Stock.is_active == True,
                (Stock.ticker.ilike(search_pattern)) | 
                (Stock.company_name.ilike(search_pattern))
            )
        ).limit(limit)
        
        result = await self.db.execute(search_query)
        return result.scalars().all()