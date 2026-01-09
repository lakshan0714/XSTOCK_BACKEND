from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.sector_repository import SectorRepository
from src.schemas.sector_schema import SectorCreate, SectorUpdate

class SectorService:
    def __init__(self, db: AsyncSession):
        self.repository = SectorRepository(db)

    async def create_sector(self, sector_data: SectorCreate, user_id: int) -> dict:
        """Create new sector"""
        try:
            # Check if name already exists
            existing = await self.repository.get_sector_by_name(sector_data.name)
            if existing:
                return {
                    "status_code": 400,
                    "error": f"Sector '{sector_data.name}' already exists"
                }

            sector_dict = sector_data.dict()
            sector_dict['created_by'] = user_id
            
            sector = await self.repository.create_sector(sector_dict)

            return {
                "status_code": 200,
                "message": "Sector created successfully",
                "data": sector
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error creating sector: {str(e)}"
            }

    async def get_all_sectors(self, active_only: bool = False) -> dict:
        """Get all sectors"""
        try:
            sectors = await self.repository.get_all_sectors(active_only)
            
            return {
                "status_code": 200,
                "data": sectors
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching sectors: {str(e)}"
            }

    async def get_sector_by_id(self, sector_id: int) -> dict:
        """Get sector by ID"""
        try:
            sector = await self.repository.get_sector_by_id(sector_id)
            if not sector:
                return {
                    "status_code": 404,
                    "error": "Sector not found"
                }

            return {
                "status_code": 200,
                "data": sector
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching sector: {str(e)}"
            }

    async def update_sector(self, sector_id: int, update_data: SectorUpdate) -> dict:
        """Update sector"""
        try:
            existing = await self.repository.get_sector_by_id(sector_id)
            if not existing:
                return {
                    "status_code": 404,
                    "error": "Sector not found"
                }

            # Check if new name already exists
            if update_data.name and update_data.name != existing.name:
                name_exists = await self.repository.get_sector_by_name(update_data.name)
                if name_exists:
                    return {
                        "status_code": 400,
                        "error": f"Sector '{update_data.name}' already exists"
                    }

            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            sector = await self.repository.update_sector(sector_id, update_dict)

            return {
                "status_code": 200,
                "message": "Sector updated successfully",
                "data": sector
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error updating sector: {str(e)}"
            }

    async def delete_sector(self, sector_id: int, hard_delete: bool = False) -> dict:
        """Delete sector"""
        try:
            if hard_delete:
                success = await self.repository.hard_delete_sector(sector_id)
            else:
                success = await self.repository.delete_sector(sector_id)

            if not success:
                return {
                    "status_code": 404,
                    "error": "Sector not found"
                }

            return {
                "status_code": 200,
                "message": "Sector deleted successfully"
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error deleting sector: {str(e)}"
            }