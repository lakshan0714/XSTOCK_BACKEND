from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.stock_repository import StockRepository
from src.repository.prediction_repository import PredictionRepository
from src.services.model_loader import model_loader
from src.services.explanation_service import ExplanationService
import numpy as np
import pandas as pd

class PredictionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.explanation_service = ExplanationService()
    
    async def predict_stock(self, ticker: str, user_id: int) -> dict:
        """Main prediction function"""
        try:
            # 1. Fetch stock data from database
            stock = await self.stock_repo.get_stock_by_ticker(ticker)
            if not stock:
                return {
                    "status_code": 404,
                    "error": f"Stock with ticker {ticker} not found"
                }
            
            # 2. Fetch calculated ratios
            ratios = await self.stock_repo.get_stock_ratios(stock.id)
            if not ratios:
                return {
                    "status_code": 400,
                    "error": "Stock ratios not calculated. Please ensure all financial data is available."
                }
            
            # 3. Prepare features for each model
            model_1_features, model_1_feature_names, model_1_feature_dict = self._prepare_model_1_features(stock)
            model_2_features, model_2_feature_names, model_2_feature_dict = self._prepare_model_2_features(ratios)
            model_3_features, model_3_feature_names, model_3_feature_dict = self._prepare_model_3_features(ratios)
            
            # 4. Run predictions
            model_1_result = self._run_model_prediction('model_1', model_1_features, model_1_feature_names, model_1_feature_dict)
            model_2_result = self._run_model_prediction('model_2', model_2_features, model_2_feature_names, model_2_feature_dict)
            model_3_result = self._run_model_prediction('model_3', model_3_features, model_3_feature_names, model_3_feature_dict)
            
            # 5. Ensemble voting
            ensemble_result = self._ensemble_voting(
                model_1_result['prediction'],
                model_2_result['prediction'],
                model_3_result['prediction'],
                model_1_result['confidence'],
                model_2_result['confidence'],
                model_3_result['confidence']
            )
            
            # 6. Get overall top features
            all_features = (
                model_1_result['top_features'] +
                model_2_result['top_features'] +
                model_3_result['top_features']
            )
            all_features.sort(key=lambda x: x['impact'], reverse=True)
            overall_top_features = all_features[:5]
            
            # 7. Generate ensemble reasoning
            ensemble_reasoning = self.explanation_service.generate_ensemble_reasoning(
                model_1_result['prediction'],
                model_2_result['prediction'],
                model_3_result['prediction'],
                ensemble_result['recommendation'],
                overall_top_features
            )
            
            # 8. Save prediction to database
            prediction_data = {
                'user_id': user_id,
                'stock_id': stock.id,
                'ticker': stock.ticker,
                'company_name': stock.company_name,
                'sector': stock.sector.name if stock.sector else None,
                
                # Model 1
                'model_1_prediction': model_1_result['prediction'],
                'model_1_confidence': model_1_result['confidence'],
                'model_1_reason': model_1_result['reason'],
                'model_1_top_features': model_1_result['top_features'],
                
                # Model 2
                'model_2_prediction': model_2_result['prediction'],
                'model_2_confidence': model_2_result['confidence'],
                'model_2_reason': model_2_result['reason'],
                'model_2_top_features': model_2_result['top_features'],
                
                # Model 3
                'model_3_prediction': model_3_result['prediction'],
                'model_3_confidence': model_3_result['confidence'],
                'model_3_reason': model_3_result['reason'],
                'model_3_top_features': model_3_result['top_features'],
                
                # Ensemble
                'final_recommendation': ensemble_result['recommendation'],
                'final_confidence': ensemble_result['confidence'],
                'final_reasoning': ensemble_reasoning,
                'overall_top_features': overall_top_features,
            }
            
            saved_prediction = await self.prediction_repo.create_prediction(prediction_data)
            
            # 9. Build response
            response = {
                "stock_info": {
                    "ticker": stock.ticker,
                    "company_name": stock.company_name,
                    "sector": stock.sector.name if stock.sector else "Unknown"
                },
                "model_1_valuation": {
                    "prediction": model_1_result['prediction'],
                    "confidence": model_1_result['confidence'],
                    "reason": model_1_result['reason'],
                    "top_features": model_1_result['top_features']
                },
                "model_2_health": {
                    "prediction": model_2_result['prediction'],
                    "confidence": model_2_result['confidence'],
                    "reason": model_2_result['reason'],
                    "top_features": model_2_result['top_features']
                },
                "model_3_growth": {
                    "prediction": model_3_result['prediction'],
                    "confidence": model_3_result['confidence'],
                    "reason": model_3_result['reason'],
                    "top_features": model_3_result['top_features']
                },
                "ensemble_prediction": {
                    "final_recommendation": ensemble_result['recommendation'],
                    "confidence": ensemble_result['confidence'],
                    "reasoning": ensemble_reasoning,
                    "overall_top_features": overall_top_features
                },
                "prediction_id": saved_prediction.id,
                "predicted_at": saved_prediction.created_at.isoformat()
            }
            
            return {
                "status_code": 200,
                "data": response
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status_code": 500,
                "error": f"Prediction error: {str(e)}"
            }
    
    def _prepare_model_1_features(self, stock):
        """
        Model 1 (Valuation) expects ONLY 5 features:
        ['pe_ratio', 'pb_ratio', 'roe', 'debt_equity', 'profit_margin']
        """
        feature_names = ['pe_ratio', 'pb_ratio', 'roe', 'debt_equity', 'profit_margin']
        
        features = []
        feature_dict = {}
        
        for name in feature_names:
            value = getattr(stock, name, 0.0) or 0.0
            features.append(value)
            feature_dict[name] = value
        
        return np.array(features).reshape(1, -1), feature_names, feature_dict
    
    def _prepare_model_2_features(self, ratios):
        """
        Model 2 (Health) expects 8 features:
        All 1-year growth and trend metrics
        """
        feature_names = [
            'revenue_growth_1y', 'ebitda_growth_1y', 'equity_growth',
            'debt_trend', 'cash_trend', 'working_capital_trend',
            'leverage_change', 'debt_to_equity_2025'
        ]
        
        features = []
        feature_dict = {}
        
        for name in feature_names:
            value = getattr(ratios, name, 0.0) or 0.0
            features.append(value)
            feature_dict[name] = value
        
        return np.array(features).reshape(1, -1), feature_names, feature_dict
    
    def _prepare_model_3_features(self, ratios):
        """
        Model 3 (Growth) expects 9 features:
        2-year CAGR, volatility, acceleration metrics
        """
        feature_names = [
            'revenue_cagr_2y', 'ebitda_cagr_2y', 'book_value_cagr_2y',
            'revenue_volatility', 'ebitda_volatility', 'revenue_acceleration',
            'ebitda_acceleration', 'capex_trend', 'working_capital_trend_2y'
        ]
        
        features = []
        feature_dict = {}
        
        for name in feature_names:
            value = getattr(ratios, name, 0.0) or 0.0
            features.append(value)
            feature_dict[name] = value
        
        return np.array(features).reshape(1, -1), feature_names, feature_dict
    
    def _run_model_prediction(self, model_key: str, features, feature_names, feature_dict):
        """Run prediction for a single model with appropriate XAI method"""
        
        model_data = model_loader.get_model(model_key)
        if not model_data:
            raise Exception(f"Model {model_key} not loaded")
        
        # Get model components
        transformer = model_data['transformer']
        label_encoder = model_data['encoder']
        model = model_data['model']
        model_type = model_data['type']
        
        # Transform features
        features_transformed = transformer.transform(features)
        
        # Predict
        prediction_idx = model.predict(features_transformed)[0]
        prediction = label_encoder.inverse_transform([prediction_idx])[0]
        
        # Get confidence
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_transformed)[0]
            confidence = float(probabilities[prediction_idx])
        else:
            confidence = 0.85
        
        # Get feature values array
        if isinstance(features, np.ndarray) and len(features.shape) > 1:
            feature_values = features[0]
        else:
            feature_values = features
        
        # Apply appropriate XAI method based on model type
        if model_type == 'xgboost':
            # Model 1: Use feature importance
            top_features, reason = self.explanation_service.explain_with_feature_importance(
                model,
                features_transformed,
                feature_names,
                feature_values
            )
            
        elif model_type == 'random_forest':
            # Model 2: Use SHAP TreeExplainer
            top_features, reason = self.explanation_service.explain_with_shap_tree(
                model,
                features_transformed,
                feature_names,
                feature_values
            )
            
        elif model_type == 'svm':
            # Model 3: Use SHAP KernelExplainer with background data
            background_data = model_data['background_data']
            top_features, reason = self.explanation_service.explain_with_shap_kernel(
                model,
                transformer,
                background_data,
                features_transformed,
                feature_names,
                feature_values
            )
        else:
            # Fallback
            top_features = []
            reason = "Prediction made successfully."
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'reason': reason,
            'top_features': top_features
        }
        
    def _calculate_simple_shap(self, model, features, feature_names):
        """Simplified SHAP calculation using feature importance"""
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            if len(importances) != len(feature_names):
                if len(importances) < len(feature_names):
                    importances = np.pad(importances, (0, len(feature_names) - len(importances)))
                else:
                    importances = importances[:len(feature_names)]
            return importances
        
        elif hasattr(model, 'coef_'):
            coefs = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
            if len(coefs) != len(feature_names):
                if len(coefs) < len(feature_names):
                    coefs = np.pad(coefs, (0, len(feature_names) - len(coefs)))
                else:
                    coefs = coefs[:len(feature_names)]
            return np.abs(coefs)
        
        else:
            return np.abs(features) / (np.abs(features).sum() + 1e-10)
    
    def _ensemble_voting(self, val_pred: str, health_pred: str, growth_pred: str, 
                        val_conf: float = 0.0, health_conf: float = 0.0, growth_conf: float = 0.0) -> dict:
        """Ensemble voting to get final BUY/SELL/HOLD recommendation"""
        print("Ensemble Voting Inputs:", val_pred, health_pred, growth_pred)
        
        val_score = {
            "undervalued": 1,
            "fair": -1,
            "overvalued": -1
        }.get(val_pred, 0)
        
        health_score = {
            "excellent": 1,
            "fair": 0,
            "poor": -1
        }.get(health_pred, 0)
        
        growth_score = {
            "strong_growth": 1,
            "moderate_growth": 1,
            "weak_growth": 0,
            "declining": -1
        }.get(growth_pred, 0)
        
        total_score = val_score + health_score + growth_score
        print(total_score)
        
        # Determine recommendation and ensemble agreement confidence
        if total_score >= 2:
            recommendation = "BUY"
            ensemble_confidence = 0.85 + (total_score - 2) * 0.05
        elif total_score <= -2:
            recommendation = "SELL"
            ensemble_confidence = 0.85 + abs(total_score + 2) * 0.05
        else:
            recommendation = "HOLD"
            ensemble_confidence = 0.75 + abs(total_score) * 0.05
        
        ensemble_confidence = min(ensemble_confidence, 0.95)
        
        # Calculate average of model confidences
        avg_model_confidence = (val_conf + health_conf + growth_conf) / 3
        
        # Combine ensemble agreement confidence with average model confidence
        final_confidence = (ensemble_confidence + avg_model_confidence) / 2
        
        return {
            "recommendation": recommendation,
            "confidence": round(final_confidence, 2)
        }
    
    async def get_user_predictions(self, user_id: int, skip: int = 0, limit: int = 50):
        """Get user's prediction history"""
        try:
            predictions = await self.prediction_repo.get_user_predictions(user_id, skip, limit)
            total = await self.prediction_repo.get_user_prediction_count(user_id)
            
            # Convert SQLAlchemy objects to dicts
            predictions_data = []
            for pred in predictions:
                predictions_data.append({
                    "id": pred.id,
                    "ticker": pred.ticker,
                    "company_name": pred.company_name,
                    "sector": pred.sector,
                    "final_recommendation": pred.final_recommendation,
                    "final_confidence": pred.final_confidence,
                    "predicted_at": pred.created_at.isoformat() if pred.created_at else None
                })
            
            return {
                "status_code": 200,
                "data": predictions_data,
                "total": total
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status_code": 500,
                "error": f"Error fetching predictions: {str(e)}"
            }
    
    async def get_prediction_by_id(self, prediction_id: int, user_id: int):
        """Get single prediction details"""
        try:
            prediction = await self.prediction_repo.get_prediction_by_id(prediction_id)
            
            if not prediction:
                return {
                    "status_code": 404,
                    "error": "Prediction not found"
                }
            
            if prediction.user_id != user_id:
                return {
                    "status_code": 403,
                    "error": "Access denied"
                }
            
            # Convert to dict
            prediction_data = {
                "id": prediction.id,
                "ticker": prediction.ticker,
                "company_name": prediction.company_name,
                "sector": prediction.sector,
                
                # Model 1
                "model_1_prediction": prediction.model_1_prediction,
                "model_1_confidence": prediction.model_1_confidence,
                "model_1_reason": prediction.model_1_reason,
                "model_1_top_features": prediction.model_1_top_features,
                
                # Model 2
                "model_2_prediction": prediction.model_2_prediction,
                "model_2_confidence": prediction.model_2_confidence,
                "model_2_reason": prediction.model_2_reason,
                "model_2_top_features": prediction.model_2_top_features,
                
                # Model 3
                "model_3_prediction": prediction.model_3_prediction,
                "model_3_confidence": prediction.model_3_confidence,
                "model_3_reason": prediction.model_3_reason,
                "model_3_top_features": prediction.model_3_top_features,
                
                # Ensemble
                "final_recommendation": prediction.final_recommendation,
                "final_confidence": prediction.final_confidence,
                "final_reasoning": prediction.final_reasoning,
                "overall_top_features": prediction.overall_top_features,
                
                "predicted_at": prediction.created_at.isoformat() if prediction.created_at else None
            }
            
            return {
                "status_code": 200,
                "data": prediction_data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status_code": 500,
                "error": f"Error fetching prediction: {str(e)}"
            }