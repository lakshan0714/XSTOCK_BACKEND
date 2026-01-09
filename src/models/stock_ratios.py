from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base

class StockRatio(Base):
    __tablename__ = "stock_ratios"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, unique=True)
    ticker = Column(String(20), index=True)
    
    # MODEL 2: Financial Health - 1-Year Changes (CALCULATED)
    revenue_growth_1y = Column(Float, nullable=True)
    ebitda_growth_1y = Column(Float, nullable=True)
    equity_growth = Column(Float, nullable=True)
    debt_trend = Column(Float, nullable=True)
    cash_trend = Column(Float, nullable=True)
    working_capital_trend = Column(Float, nullable=True)
    leverage_change = Column(Float, nullable=True)
    debt_to_equity_2025 = Column(Float, nullable=True)
    
    # MODEL 3: Growth Trajectory - 2-Year Metrics (CALCULATED)
    revenue_cagr_2y = Column(Float, nullable=True)
    ebitda_cagr_2y = Column(Float, nullable=True)
    book_value_cagr_2y = Column(Float, nullable=True)
    revenue_volatility = Column(Float, nullable=True)
    ebitda_volatility = Column(Float, nullable=True)
    revenue_acceleration = Column(Float, nullable=True)
    ebitda_acceleration = Column(Float, nullable=True)
    capex_trend = Column(Float, nullable=True)
    working_capital_trend_2y = Column(Float, nullable=True)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    stock = relationship("Stock", backref="ratios")