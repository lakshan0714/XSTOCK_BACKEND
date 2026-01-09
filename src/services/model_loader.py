import joblib
import os
from pathlib import Path

class ModelLoader:
    def __init__(self):
        self.models = {}
        
        self.base_path = Path(__file__).parent.parent / "AI_models"
        
       
        
        if not self.base_path.exists():
            print(f"❌ AI_models folder not found at: {self.base_path.absolute()}")
        else:
            print(f" Found AI_models folder")
        
    def load_models(self):
        """Load all 3 models with their encoders and transformers"""
        
        if not self.base_path.exists():
            print("❌ Cannot load models: AI_models folder not found")
            return False
        
        try:
          
            
            # Model 1: Valuation
            print("\n🔄 Loading Model 1 (Valuation)...")
            model_1_path = self.base_path / "model_1"
            
            if not model_1_path.exists():
                print(f"❌ Model 1 folder not found: {model_1_path}")
                return False
            
       
            
            self.models['model_1'] = {
                'encoder': joblib.load(model_1_path / "label_encoder.pkl"),
                'transformer': joblib.load(model_1_path / "model1_transformer.pkl"),
                'model': joblib.load(model_1_path / "model1_fundamental_valuation.pkl"),
                'name': 'Valuation Model',
                'type': 'xgboost',
                'classes': ['UNDERVALUED', 'FAIR', 'OVERVALUED']
            }
            print(" Model 1 loaded")
            
            # Model 2: Health
            print("\n Loading Model 2 (Health)...")
            model_2_path = self.base_path / "model_2"
            
            if not model_2_path.exists():
                print(f"❌ Model 2 folder not found: {model_2_path}")
                return False
            
            self.models['model_2'] = {
                'encoder': joblib.load(model_2_path / "model2_label_encoder.pkl"),
                'transformer': joblib.load(model_2_path / "model2_transformer.pkl"),
                'model': joblib.load(model_2_path / "model2_financial_health.pkl"),
                'name': 'Financial Health Model',
                'type': 'random_forest',
                'classes': ['EXCELLENT', 'FAIR', 'POOR']
            }
            print(" Model 2 loaded")
            
            # Model 3: Growth
            print("\n🔄 Loading Model 3 (Growth)...")
            model_3_path = self.base_path / "model_3"
            
            if not model_3_path.exists():
                print(f"❌ Model 3 folder not found: {model_3_path}")
                return False
            # Load background data for SHAP KernelExplainer
            background_data_full = joblib.load(model_3_path / "background_data.pkl")
           # print(f"   📊 Background data loaded: {background_data.shape}")
            # Use only first 30 samples for speed
            background_data = background_data_full[:30]

            self.models['model_3'] = {
                'encoder': joblib.load(model_3_path / "model3_label_encoder.pkl"),
                'transformer': joblib.load(model_3_path / "model3_transformer.pkl"),
                'model': joblib.load(model_3_path / "model3_growth.pkl"),
                'background_data': background_data,
                'name': 'Growth Trajectory Model',
                'type': 'svm',
                'classes': ['STRONG_GROWTH', 'MODERATE_GROWTH', 'WEAK_GROWTH', 'DECLINING']
            }
            print(" Model 3 loaded")
            
            print("\n All ML models loaded successfully!")
            return True
            
        except FileNotFoundError as e:
            print(f"\n❌ File not found: {e}")
            print("Please check your file names match exactly:")
            print("  - encoder.pkl")
            print("  - transformer.pkl")
            print("  - model.pkl")
            return False
        except Exception as e:
            print(f"\n❌ Error loading models: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_model(self, model_key: str):
        """Get specific model"""
        return self.models.get(model_key)
    
    def health_check(self):
        """Check if all models are loaded"""
        return all(key in self.models for key in ['model_1', 'model_2', 'model_3'])

# Global model loader instance
model_loader = ModelLoader()