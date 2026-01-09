from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StockCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    company_name: str = Field(..., min_length=1, max_length=255)
    sector_id: int
    
    # MODEL 1: Fundamental Ratios (User provides these)
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    eps: Optional[float] = None
    current_price: Optional[float] = None
    price_1year_ago: Optional[float] = None
    
    # Growth Data - 2023
    revenue_per_share_2023: Optional[float] = None
    ebitda_per_share_2023: Optional[float] = None
    book_value_per_share_2023: Optional[float] = None
    debt_per_share_2023: Optional[float] = None
    cash_per_share_2023: Optional[float] = None
    working_capital_per_share_2023: Optional[float] = None
    capex_per_share_2023: Optional[float] = None
    
    # Growth Data - 2024
    revenue_per_share_2024: Optional[float] = None
    ebitda_per_share_2024: Optional[float] = None
    book_value_per_share_2024: Optional[float] = None
    debt_per_share_2024: Optional[float] = None
    cash_per_share_2024: Optional[float] = None
    working_capital_per_share_2024: Optional[float] = None
    capex_per_share_2024: Optional[float] = None
    
    # Growth Data - 2025
    revenue_per_share_2025: Optional[float] = None
    ebitda_per_share_2025: Optional[float] = None
    book_value_per_share_2025: Optional[float] = None
    debt_per_share_2025: Optional[float] = None
    cash_per_share_2025: Optional[float] = None
    working_capital_per_share_2025: Optional[float] = None
    capex_per_share_2025: Optional[float] = None


class StockUpdate(BaseModel):
    company_name: Optional[str] = None
    sector_id: Optional[int] = None
    
    # MODEL 1: Fundamental Ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    profit_margin: Optional[float] = None
    debt_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    eps: Optional[float] = None
    current_price: Optional[float] = None
    price_1year_ago: Optional[float] = None
    
    # Growth Data - 2023
    revenue_per_share_2023: Optional[float] = None
    ebitda_per_share_2023: Optional[float] = None
    book_value_per_share_2023: Optional[float] = None
    debt_per_share_2023: Optional[float] = None
    cash_per_share_2023: Optional[float] = None
    working_capital_per_share_2023: Optional[float] = None
    capex_per_share_2023: Optional[float] = None
    
    # Growth Data - 2024
    revenue_per_share_2024: Optional[float] = None
    ebitda_per_share_2024: Optional[float] = None
    book_value_per_share_2024: Optional[float] = None
    debt_per_share_2024: Optional[float] = None
    cash_per_share_2024: Optional[float] = None
    working_capital_per_share_2024: Optional[float] = None
    capex_per_share_2024: Optional[float] = None
    
    # Growth Data - 2025
    revenue_per_share_2025: Optional[float] = None
    ebitda_per_share_2025: Optional[float] = None
    book_value_per_share_2025: Optional[float] = None
    debt_per_share_2025: Optional[float] = None
    cash_per_share_2025: Optional[float] = None
    working_capital_per_share_2025: Optional[float] = None
    capex_per_share_2025: Optional[float] = None
    
    is_active: Optional[bool] = None


class StockResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    sector_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockDetailResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    sector_id: int
    
    # Model 1 - Fundamental Ratios
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    roe: Optional[float]
    profit_margin: Optional[float]
    debt_equity: Optional[float]
    current_ratio: Optional[float]
    eps: Optional[float]
    current_price: Optional[float]
    price_1year_ago: Optional[float]
    
    # Growth Data - 2023
    revenue_per_share_2023: Optional[float]
    ebitda_per_share_2023: Optional[float]
    book_value_per_share_2023: Optional[float]
    debt_per_share_2023: Optional[float]
    cash_per_share_2023: Optional[float]
    working_capital_per_share_2023: Optional[float]
    capex_per_share_2023: Optional[float]
    
    # Growth Data - 2024
    revenue_per_share_2024: Optional[float]
    ebitda_per_share_2024: Optional[float]
    book_value_per_share_2024: Optional[float]
    debt_per_share_2024: Optional[float]
    cash_per_share_2024: Optional[float]
    working_capital_per_share_2024: Optional[float]
    capex_per_share_2024: Optional[float]
    
    # Growth Data - 2025
    revenue_per_share_2025: Optional[float]
    ebitda_per_share_2025: Optional[float]
    book_value_per_share_2025: Optional[float]
    debt_per_share_2025: Optional[float]
    cash_per_share_2025: Optional[float]
    working_capital_per_share_2025: Optional[float]
    capex_per_share_2025: Optional[float]
    
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockWithRatiosResponse(BaseModel):
    stock: StockDetailResponse
    ratios: Optional[dict]  # Calculated ratios from stock_ratios table
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_stocks: int
    total_companies: int
    active_stocks: int
    inactive_stocks: int
    sector_distribution: list
    recent_activities: list