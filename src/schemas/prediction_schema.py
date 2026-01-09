from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FeatureImportance(BaseModel):
    name: str
    value: float
    impact: float

class ModelPrediction(BaseModel):
    prediction: str
    confidence: float
    reason: str
    top_features: List[FeatureImportance]

class StockInfo(BaseModel):
    ticker: str
    company_name: str
    sector: str

class PredictionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")

class PredictionResponse(BaseModel):
    stock_info: StockInfo
    model_1_valuation: ModelPrediction
    model_2_health: ModelPrediction
    model_3_growth: ModelPrediction
    ensemble_prediction: dict
    prediction_id: int
    predicted_at: datetime
    
    class Config:
        from_attributes = True

class PredictionHistoryItem(BaseModel):
    id: int
    ticker: str
    company_name: str
    final_recommendation: str
    final_confidence: float
    predicted_at: datetime
    
    class Config:
        from_attributes = True

class PredictionDetailResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    sector: str
    
    model_1_prediction: str
    model_1_confidence: float
    model_1_reason: str
    
    model_2_prediction: str
    model_2_confidence: float
    model_2_reason: str
    
    model_3_prediction: str
    model_3_confidence: float
    model_3_reason: str
    
    final_recommendation: str
    final_confidence: float
    final_reasoning: str
    
    predicted_at: datetime
    
    class Config:
        from_attributes = True

class PredictionStats(BaseModel):
    total_predictions: int
    buy_count: int
    sell_count: int
    hold_count: int
    buy_percentage: float
    sell_percentage: float
    hold_percentage: float
    average_confidence: float

class SectorPredictionStats(BaseModel):
    sector: str
    total: int
    buy: int
    sell: int
    hold: int
    avg_confidence: float

class TopPredictedStock(BaseModel):
    ticker: str
    company_name: str
    prediction_count: int
    most_common_prediction: str
    most_common_count: int