from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from src.models.sector import Sector
from typing import List, Optional

class SectorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sector(self, sector_data: dict) -> Sector:
        """Create a new sector"""
        sector = Sector(**sector_data)
        self.db.add(sector)
        await self.db.commit()
        await self.db.refresh(sector)
        return sector

    async def get_sector_by_id(self, sector_id: int) -> Optional[Sector]:
        """Get sector by ID"""
        result = await self.db.execute(
            select(Sector).where(Sector.id == sector_id)
        )
        return result.scalar_one_or_none()

    async def get_sector_by_name(self, name: str) -> Optional[Sector]:
        """Get sector by name"""
        result = await self.db.execute(
            select(Sector).where(Sector.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_sectors(self, active_only: bool = False) -> List[Sector]:
        """Get all sectors"""
        query = select(Sector)
        
        if active_only:
            query = query.where(Sector.is_active == True)
        
        query = query.order_by(Sector.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_sector(self, sector_id: int, update_data: dict) -> Optional[Sector]:
        """Update sector"""
        sector = await self.get_sector_by_id(sector_id)
        if not sector:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(sector, key):
                setattr(sector, key, value)
        
        await self.db.commit()
        await self.db.refresh(sector)
        return sector

    async def delete_sector(self, sector_id: int) -> bool:
        """Soft delete sector"""
        sector = await self.get_sector_by_id(sector_id)
        if not sector:
            return False
        
        sector.is_active = False
        await self.db.commit()
        return True

    async def hard_delete_sector(self, sector_id: int) -> bool:
        """Hard delete sector"""
        sector = await self.get_sector_by_id(sector_id)
        if not sector:
            return False
        
        await self.db.delete(sector)
        await self.db.commit()
        return True

    async def get_sector_count(self) -> int:
        """Get total sector count"""
        result = await self.db.execute(select(func.count(Sector.id)))
        return result.scalar()