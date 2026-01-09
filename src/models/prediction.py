from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    ticker = Column(String(20), index=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    
    # Model 1: Valuation
    model_1_prediction = Column(String(20))  # UNDERVALUED, FAIR, OVERVALUED
    model_1_confidence = Column(Float)
    model_1_reason = Column(Text)
    model_1_top_features = Column(JSON)  # [{name, value, impact}, ...]
    
    # Model 2: Health
    model_2_prediction = Column(String(20))  # EXCELLENT, FAIR, POOR
    model_2_confidence = Column(Float)
    model_2_reason = Column(Text)
    model_2_top_features = Column(JSON)
    
    # Model 3: Growth
    model_3_prediction = Column(String(30))  # STRONG_GROWTH, MODERATE_GROWTH, WEAK_GROWTH, DECLINING
    model_3_confidence = Column(Float)
    model_3_reason = Column(Text)
    model_3_top_features = Column(JSON)
    
    # Ensemble
    final_recommendation = Column(String(10))  # BUY, SELL, HOLD
    final_confidence = Column(Float)
    final_reasoning = Column(Text)
    overall_top_features = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="predictions")
    stock = relationship("Stock", backref="predictions")