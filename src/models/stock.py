from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=False)
    
    # MODEL 1: Fundamental Ratios (User Input - from fundamental.csv)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)
    debt_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    price_1year_ago = Column(Float, nullable=True)
    
    # Growth Data - Financial metrics for 2023 (User Input - from growth.csv)
    revenue_per_share_2023 = Column(Float, nullable=True)
    ebitda_per_share_2023 = Column(Float, nullable=True)
    book_value_per_share_2023 = Column(Float, nullable=True)
    debt_per_share_2023 = Column(Float, nullable=True)
    cash_per_share_2023 = Column(Float, nullable=True)
    working_capital_per_share_2023 = Column(Float, nullable=True)
    capex_per_share_2023 = Column(Float, nullable=True)
    
    # Growth Data - Financial metrics for 2024 (User Input - from growth.csv)
    revenue_per_share_2024 = Column(Float, nullable=True)
    ebitda_per_share_2024 = Column(Float, nullable=True)
    book_value_per_share_2024 = Column(Float, nullable=True)
    debt_per_share_2024 = Column(Float, nullable=True)
    cash_per_share_2024 = Column(Float, nullable=True)
    working_capital_per_share_2024 = Column(Float, nullable=True)
    capex_per_share_2024 = Column(Float, nullable=True)
    
    # Growth Data - Financial metrics for 2025 (User Input - from growth.csv)
    revenue_per_share_2025 = Column(Float, nullable=True)
    ebitda_per_share_2025 = Column(Float, nullable=True)
    book_value_per_share_2025 = Column(Float, nullable=True)
    debt_per_share_2025 = Column(Float, nullable=True)
    cash_per_share_2025 = Column(Float, nullable=True)
    working_capital_per_share_2025 = Column(Float, nullable=True)
    capex_per_share_2025 = Column(Float, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    
    # Relationships
    sector = relationship("Sector", backref="stocks")