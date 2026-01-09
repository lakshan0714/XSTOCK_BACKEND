from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.stock_repository import StockRepository
from src.schemas.stock_schema import StockCreate, StockUpdate
from typing import Optional
import math

class StockService:
    def __init__(self, db: AsyncSession):
        self.repository = StockRepository(db)

    async def create_stock(self, stock_data: StockCreate, user_id: int) -> dict:
        """Create stock and calculate Model 2 & 3 ratios"""
        try:
            # Check if ticker already exists
            existing = await self.repository.get_stock_by_ticker(stock_data.ticker)
            if existing:
                return {
                    "status_code": 400,
                    "error": f"Stock with ticker {stock_data.ticker} already exists"
                }

            # Create stock (Model 1 ratios from user input)
            stock_dict = stock_data.dict()
            stock_dict['ticker'] = stock_data.ticker.upper()
            stock_dict['created_by'] = user_id
            
            stock = await self.repository.create_stock(stock_dict)

            # Calculate and store Model 2 & 3 ratios
            await self._calculate_and_store_ratios(stock)

            # Convert to dict for JSON serialization
            stock_response = {
                "id": stock.id,
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "sector_id": stock.sector_id,
                "is_active": stock.is_active,
                "created_at": stock.created_at.isoformat() if stock.created_at else None
            }

            return {
                "status_code": 200,
                "message": "Stock created successfully",
                "data": stock_response
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error creating stock: {str(e)}"
            }

    async def get_stock_by_id(self, stock_id: int) -> dict:
        """Get stock by ID with ratios"""
        try:
            result = await self.repository.get_stock_with_ratios(stock_id)
            if not result:
                return {
                    "status_code": 404,
                    "error": "Stock not found"
                }

            stock = result["stock"]
            ratios = result["ratios"]

            # Convert stock to dict
            stock_data = {
                "id": stock.id,
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "sector_id": stock.sector_id,
                "sector_name": stock.sector.name if stock.sector else None,
                "is_active": stock.is_active,
                "created_at": stock.created_at.isoformat() if stock.created_at else None,
                # Model 1 ratios
                "pe_ratio": stock.pe_ratio,
                "pb_ratio": stock.pb_ratio,
                "roe": stock.roe,
                "profit_margin": stock.profit_margin,
                "debt_equity": stock.debt_equity,
                "current_ratio": stock.current_ratio,
                "eps": stock.eps,
                "current_price": stock.current_price,
                "price_1year_ago": stock.price_1year_ago,
            }

            # Convert ratios to dict
            ratios_data = None
            if ratios:
                ratios_data = {
                    "revenue_growth_1y": ratios.revenue_growth_1y,
                    "ebitda_growth_1y": ratios.ebitda_growth_1y,
                    "equity_growth": ratios.equity_growth,
                    "debt_trend": ratios.debt_trend,
                    "cash_trend": ratios.cash_trend,
                    "working_capital_trend": ratios.working_capital_trend,
                    "leverage_change": ratios.leverage_change,
                    "debt_to_equity_2025": ratios.debt_to_equity_2025,
                    "revenue_cagr_2y": ratios.revenue_cagr_2y,
                    "ebitda_cagr_2y": ratios.ebitda_cagr_2y,
                    "book_value_cagr_2y": ratios.book_value_cagr_2y,
                    "revenue_volatility": ratios.revenue_volatility,
                    "ebitda_volatility": ratios.ebitda_volatility,
                    "revenue_acceleration": ratios.revenue_acceleration,
                    "ebitda_acceleration": ratios.ebitda_acceleration,
                    "capex_trend": ratios.capex_trend,
                    "working_capital_trend_2y": ratios.working_capital_trend_2y,
                }

            return {
                "status_code": 200,
                "data": {
                    "stock": stock_data,
                    "ratios": ratios_data
                }
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching stock: {str(e)}"
            }

    async def get_stock_by_ticker(self, ticker: str) -> dict:
        """Get stock by ticker with ratios"""
        try:
            stock = await self.repository.get_stock_by_ticker(ticker)
            if not stock:
                return {
                    "status_code": 404,
                    "error": "Stock not found"
                }

            ratios = await self.repository.get_stock_ratios(stock.id)

            # Convert to dict
            stock_data = {
                "id": stock.id,
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "sector_id": stock.sector_id,
                "sector_name": stock.sector.name if stock.sector else None,
                "pe_ratio": stock.pe_ratio,
                "pb_ratio": stock.pb_ratio,
                "roe": stock.roe,
                "profit_margin": stock.profit_margin,
                "debt_equity": stock.debt_equity,
                "current_ratio": stock.current_ratio,
                "eps": stock.eps,
                "current_price": stock.current_price,
                "price_1year_ago": stock.price_1year_ago,
            }

            ratios_data = None
            if ratios:
               ratios_data = {
                    "revenue_growth_1y": ratios.revenue_growth_1y,
                    "ebitda_growth_1y": ratios.ebitda_growth_1y,
                    "equity_growth": ratios.equity_growth,
                    "debt_trend": ratios.debt_trend,
                    "cash_trend": ratios.cash_trend,
                    "working_capital_trend": ratios.working_capital_trend,
                    "leverage_change": ratios.leverage_change,
                    "debt_to_equity_2025": ratios.debt_to_equity_2025,
                    "revenue_cagr_2y": ratios.revenue_cagr_2y,
                    "ebitda_cagr_2y": ratios.ebitda_cagr_2y,
                    "book_value_cagr_2y": ratios.book_value_cagr_2y,
                    "revenue_volatility": ratios.revenue_volatility,
                    "ebitda_volatility": ratios.ebitda_volatility,
                    "revenue_acceleration": ratios.revenue_acceleration,
                    "ebitda_acceleration": ratios.ebitda_acceleration,
                    "capex_trend": ratios.capex_trend,
                    "working_capital_trend_2y": ratios.working_capital_trend_2y,
                }

            return {
                "status_code": 200,
                "data": {
                    "stock": stock_data,
                    "ratios": ratios_data
                }
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching stock: {str(e)}"
            }

    async def get_all_stocks(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = False,
        sector_id: Optional[int] = None
    ) -> dict:
        """Get all stocks with pagination"""
        try:
            stocks = await self.repository.get_all_stocks(skip, limit, active_only, sector_id)
            total = await self.repository.get_total_stocks(active_only)

            # Convert stocks to list of dicts
            stocks_data = [
                {
                    "id": stock.id,
                    "ticker": stock.ticker,
                    "company_name": stock.company_name,
                    "sector_id": stock.sector_id,
                    "sector_name": stock.sector.name if stock.sector else None,
                    "is_active": stock.is_active,
                    "created_at": stock.created_at.isoformat() if stock.created_at else None
                  
                }
                for stock in stocks
            ]

            return {
                "status_code": 200,
                "data": stocks_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching stocks: {str(e)}"
            }

    async def update_stock(self, stock_id: int, update_data: StockUpdate) -> dict:
        """Update stock and recalculate ratios"""
        try:
            existing = await self.repository.get_stock_by_id(stock_id)
            if not existing:
                return {
                    "status_code": 404,
                    "error": "Stock not found"
                }

            # Update stock
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            stock = await self.repository.update_stock(stock_id, update_dict)

            # Recalculate Model 2 & 3 ratios
            await self._calculate_and_store_ratios(stock)

            # Convert to dict
            stock_response = {
                "id": stock.id,
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "sector_id": stock.sector_id,
                "is_active": stock.is_active,
                "updated_at": stock.updated_at.isoformat() if stock.updated_at else None
            }

            return {
                "status_code": 200,
                "message": "Stock updated successfully",
                "data": stock_response
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error updating stock: {str(e)}"
            }

    async def delete_stock(self, stock_id: int, hard_delete: bool = False) -> dict:
        """Delete stock (soft or hard)"""
        try:
            if hard_delete:
                success = await self.repository.hard_delete_stock(stock_id)
            else:
                success = await self.repository.delete_stock(stock_id)

            if not success:
                return {
                    "status_code": 404,
                    "error": "Stock not found"
                }

            return {
                "status_code": 200,
                "message": "Stock deleted successfully"
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error deleting stock: {str(e)}"
            }

    async def search_stocks(self, query: str) -> dict:
        """Search stocks by ticker or company name"""
        try:
            stocks = await self.repository.search_stocks(query)
            
            # Convert to dicts
            stocks_data = [
                {
                    "id": stock.id,
                    "ticker": stock.ticker,
                    "company_name": stock.company_name,
                    "sector_name": stock.sector.name if stock.sector else None,
                }
                for stock in stocks
            ]

            return {
                "status_code": 200,
                "data": stocks_data
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error searching stocks: {str(e)}"
            }

    async def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics"""
        try:
            total_stocks = await self.repository.get_total_stocks()
            active_stocks = await self.repository.get_active_stocks_count()
            sector_distribution = await self.repository.get_sector_distribution()
            recent_stocks = await self.repository.get_recent_stocks(10)

            return {
                "status_code": 200,
                "data": {
                    "total_stocks": total_stocks,
                    "total_companies": total_stocks,
                    "active_stocks": active_stocks,
                    "inactive_stocks": total_stocks - active_stocks,
                    "sector_distribution": sector_distribution,
                    "recent_activities": [
                        {
                            "id": stock.id,
                            "ticker": stock.ticker,
                            "company_name": stock.company_name,
                            "sector": stock.sector.name if stock.sector else "Unknown",
                            "created_at": stock.created_at.isoformat() if stock.created_at else None
                        }
                        for stock in recent_stocks
                    ]
                }
            }

        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Error fetching dashboard stats: {str(e)}"
            }

    # ==================== RATIO CALCULATION (MODEL 2 & 3 ONLY) ====================
    
    async def _calculate_and_store_ratios(self, stock) -> None:
        """Calculate Model 2 & 3 ratios (Model 1 comes from user)"""
        ratios = {}

        # Helper functions
        def safe_growth(new_val, old_val, default=0.0):
            if new_val is None or old_val is None or old_val == 0:
                return default
            return ((new_val - old_val) / old_val) 

        def safe_cagr(end_val, start_val, periods=2, default=0.0):
            if end_val is None or start_val is None or start_val <= 0 or end_val <= 0:
                return default
            try:
                return (pow(end_val / start_val, 1 / periods) - 1) 
            except:
                return default

        def safe_calc(numerator, denominator, default=None):
            if numerator is None or denominator is None or denominator == 0:
                return default
            return numerator / denominator

        # ========== MODEL 2: FINANCIAL HEALTH (1-YEAR CHANGES) ==========
        
        ratios['revenue_growth_1y'] = safe_growth(
            stock.revenue_per_share_2025,
            stock.revenue_per_share_2024
        )

        ratios['ebitda_growth_1y'] = safe_growth(
            stock.ebitda_per_share_2025,
            stock.ebitda_per_share_2024
        )

        ratios['equity_growth'] = safe_growth(
            stock.book_value_per_share_2025,
            stock.book_value_per_share_2024
        )

        ratios['debt_trend'] = safe_growth(
            stock.debt_per_share_2025,
            stock.debt_per_share_2024
        )

        ratios['cash_trend'] = safe_growth(
            stock.cash_per_share_2025,
            stock.cash_per_share_2024
        )

        ratios['working_capital_trend'] = safe_growth(
            stock.working_capital_per_share_2025,
            stock.working_capital_per_share_2024
        )

        # Leverage Change
        debt_equity_2024 = safe_calc(
            stock.debt_per_share_2024,
            stock.book_value_per_share_2024
        )
        debt_equity_2025 = safe_calc(
            stock.debt_per_share_2025,
            stock.book_value_per_share_2025
        )
        
        if debt_equity_2024 is not None and debt_equity_2025 is not None:
            ratios['leverage_change'] = debt_equity_2025 - debt_equity_2024
        else:
            ratios['leverage_change'] = None

        ratios['debt_to_equity_2025'] = debt_equity_2025

        # ========== MODEL 3: GROWTH TRAJECTORY (2-YEAR METRICS) ==========
        
        ratios['revenue_cagr_2y'] = safe_cagr(
            stock.revenue_per_share_2025,
            stock.revenue_per_share_2023,
            2
        )

        ratios['ebitda_cagr_2y'] = safe_cagr(
            stock.ebitda_per_share_2025,
            stock.ebitda_per_share_2023,
            2
        )

        ratios['book_value_cagr_2y'] = safe_cagr(
            stock.book_value_per_share_2025,
            stock.book_value_per_share_2023,
            2
        )

        # Revenue Volatility
        growth_2023_2024 = safe_growth(
            stock.revenue_per_share_2024,
            stock.revenue_per_share_2023
        )
        growth_2024_2025 = safe_growth(
            stock.revenue_per_share_2025,
            stock.revenue_per_share_2024
        )
        
        if growth_2023_2024 is not None and growth_2024_2025 is not None:
            mean_growth = (growth_2023_2024 + growth_2024_2025) / 2
            variance = ((growth_2023_2024 - mean_growth) ** 2 + 
                       (growth_2024_2025 - mean_growth) ** 2) / 2
            ratios['revenue_volatility'] = math.sqrt(variance) if variance >= 0 else 0.0
        else:
            ratios['revenue_volatility'] = None

        # EBITDA Volatility
        ebitda_growth_2023_2024 = safe_growth(
            stock.ebitda_per_share_2024,
            stock.ebitda_per_share_2023
        )
        ebitda_growth_2024_2025 = safe_growth(
            stock.ebitda_per_share_2025,
            stock.ebitda_per_share_2024
        )
        
        if ebitda_growth_2023_2024 is not None and ebitda_growth_2024_2025 is not None:
            mean_ebitda_growth = (ebitda_growth_2023_2024 + ebitda_growth_2024_2025) / 2
            ebitda_variance = ((ebitda_growth_2023_2024 - mean_ebitda_growth) ** 2 + 
                              (ebitda_growth_2024_2025 - mean_ebitda_growth) ** 2) / 2
            ratios['ebitda_volatility'] = math.sqrt(ebitda_variance) if ebitda_variance >= 0 else 0.0
        else:
            ratios['ebitda_volatility'] = None

        # Revenue Acceleration
        if growth_2023_2024 is not None and growth_2024_2025 is not None:
            ratios['revenue_acceleration'] = growth_2024_2025 - growth_2023_2024
        else:
            ratios['revenue_acceleration'] = None

        # EBITDA Acceleration
        if ebitda_growth_2023_2024 is not None and ebitda_growth_2024_2025 is not None:
            ratios['ebitda_acceleration'] = ebitda_growth_2024_2025 - ebitda_growth_2023_2024
        else:
            ratios['ebitda_acceleration'] = None

        # CapEx Trend
        ratios['capex_trend'] = safe_growth(
            stock.capex_per_share_2025,
            stock.capex_per_share_2024
        )

        # Working Capital Trend (2-year)
        ratios['working_capital_trend_2y'] = safe_cagr(
            stock.working_capital_per_share_2025,
            stock.working_capital_per_share_2023,
            2
        )

        # Add ticker (NOT stock_id)
        ratios['ticker'] = stock.ticker

        # Store or update ratios
        await self.repository.update_stock_ratios(stock.id, ratios)