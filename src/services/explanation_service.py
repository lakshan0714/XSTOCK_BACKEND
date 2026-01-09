import numpy as np
import shap


class ExplanationService:
    
    # Feature name mapping for better readability
    FEATURE_NAMES = {
        # Model 1
        'pe_ratio': 'PE Ratio',
        'pb_ratio': 'PB Ratio',
        'roe': 'Return on Equity (ROE)',
        'profit_margin': 'Profit Margin',
        'debt_equity': 'Debt to Equity',
        
        # Model 2
        'revenue_growth_1y': '1-Year Revenue Growth',
        'ebitda_growth_1y': '1-Year EBITDA Growth',
        'equity_growth': 'Equity Growth',
        'debt_trend': 'Debt Trend',
        'cash_trend': 'Cash Trend',
        'working_capital_trend': 'Working Capital Trend',
        'leverage_change': 'Leverage Change',
        'debt_to_equity_2025': 'Current Debt/Equity Ratio',
        
        # Model 3
        'revenue_cagr_2y': '2-Year Revenue CAGR',
        'ebitda_cagr_2y': '2-Year EBITDA CAGR',
        'book_value_cagr_2y': '2-Year Book Value CAGR',
        'revenue_volatility': 'Revenue Volatility',
        'ebitda_volatility': 'EBITDA Volatility',
        'revenue_acceleration': 'Revenue Acceleration',
        'ebitda_acceleration': 'EBITDA Acceleration',
        'capex_trend': 'CapEx Trend',
        'working_capital_trend_2y': '2-Year Working Capital Trend',
    }
    
    def explain_with_feature_importance(self, model, features_transformed, feature_names, feature_values):
        """
        Model 1 (XGBoost): Use built-in feature_importances_
        Returns: top features with importance values
        """
        try:
            # Get feature importances from trained model
            importances = model.feature_importances_
            
            # Get top 3 features
            top_indices = np.argsort(importances)[-3:][::-1]
            
            top_features = []
            for idx in top_indices:
                top_features.append({
                    'name': feature_names[idx],
                    'value': float(feature_values[idx]),
                    'impact': float(importances[idx])
                })
            
            # Generate explanation
            explanation = self._format_feature_importance_explanation(
                top_features, 
                feature_values,
                feature_names
            )
            
            return top_features, explanation
            
        except Exception as e:
            print(f"Feature importance error: {e}")
            # Fallback
            return [], "Unable to generate explanation."
    
    def explain_with_shap_tree(self, model, features_transformed, feature_names, feature_values):
        """
        Model 2 (Random Forest): Use SHAP TreeExplainer
        Returns: top features with SHAP values
        """
        try:
            # Create TreeExplainer
            explainer = shap.TreeExplainer(model)
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(features_transformed)
            
            # For multi-class, shap_values is a list of arrays (one per class)
            # We take the SHAP values for the predicted class
            if isinstance(shap_values, list):
                # Get prediction to know which class SHAP values to use
                prediction_idx = model.predict(features_transformed)[0]
                shap_values_for_prediction = shap_values[prediction_idx][0]
            else:
                shap_values_for_prediction = shap_values[0]
            
            # Get top 3 features by absolute SHAP value
            abs_shap = np.abs(shap_values_for_prediction)
            top_indices = np.argsort(abs_shap)[-3:][::-1]
            
            top_features = []
            for idx in top_indices:
                top_features.append({
                    'name': feature_names[idx],
                    'value': float(feature_values[idx]),
                    'impact': float(abs_shap[idx])
                })
            
            # Generate explanation
            explanation = self._format_shap_explanation(
                top_features,
                shap_values_for_prediction,
                feature_names,
                feature_values
            )
            
            return top_features, explanation
            
        except Exception as e:
            print(f" SHAP Tree error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to feature importance
            return self.explain_with_feature_importance(model, features_transformed, feature_names, feature_values)
    
    def explain_with_shap_kernel(self, model, transformer, background_data, features_transformed, feature_names, feature_values):
        """
        Model 3 (SVM): Use SHAP KernelExplainer with background data
        Returns: top features with SHAP values
        """
        print("\n" + "="*60)
        print("🔍 MODEL 3 SHAP EXPLANATION - DEBUG INFO")
        print("="*60)
        
        try:
            print(f"📊 Background data shape: {background_data.shape}")
            print(f"📊 Features shape: {features_transformed.shape}")
            print(f"📊 Model type: {type(model).__name__}")
            
            # Check if model has predict_proba
            if not hasattr(model, 'predict_proba'):
                print("❌ Model doesn't have predict_proba method!")
                raise Exception("Model doesn't support probability predictions")
            
            # Test prediction
            test_pred = model.predict(features_transformed)
            print(f"✅ Test prediction: {test_pred}")
            
            # Reduce background data if too large
            if background_data.shape[0] > 30:
                print(f"⚠️  Reducing background data from {background_data.shape[0]} to 30 samples")
                indices = np.random.choice(background_data.shape[0], 30, replace=False)
                background_data = background_data[indices]
            
            # Create prediction function
            def predict_fn(X):
                return model.predict_proba(X)
            
            # Create KernelExplainer
            print(f"\n🔄 Creating KernelExplainer with {background_data.shape[0]} samples...")
            explainer = shap.KernelExplainer(predict_fn, background_data, link="identity")
            print("✅ KernelExplainer created")
            
            # Calculate SHAP values
            print("\n⏳ Calculating SHAP values (nsamples=50)...")
            shap_values = explainer.shap_values(features_transformed, nsamples=50)
            
            print(f"✅ SHAP values calculated!")
            print(f"   Shape: {shap_values.shape}")
            
            # Get predicted class
            prediction_idx = test_pred[0]
            print(f"📍 Predicted class index: {prediction_idx}")
            
            # Extract SHAP values for the predicted class
            # Shape is (1, 9, 4) -> we want (9,) for the predicted class
            if len(shap_values.shape) == 3:
                # Multi-class: (samples, features, classes)
                shap_values_for_prediction = shap_values[0, :, prediction_idx]
            elif len(shap_values.shape) == 2:
                # Binary or already extracted: (samples, features)
                shap_values_for_prediction = shap_values[0, :]
            else:
                raise ValueError(f"Unexpected SHAP values shape: {shap_values.shape}")
            
            print(f"✅ SHAP values for predicted class: {shap_values_for_prediction}")
            
            # Get top 3 features by absolute SHAP value
            abs_shap = np.abs(shap_values_for_prediction)
            top_indices = np.argsort(abs_shap)[-3:][::-1]
            
            print(f"\n🏆 Top 3 features:")
            top_features = []
            for idx in top_indices:
                feature_info = {
                    'name': feature_names[idx],
                    'value': float(feature_values[idx]),
                    'impact': float(abs_shap[idx])
                }
                top_features.append(feature_info)
                print(f"   {feature_names[idx]}: value={feature_values[idx]:.3f}, SHAP={shap_values_for_prediction[idx]:.3f}, impact={abs_shap[idx]:.3f}")
            
            # Generate explanation
            explanation = self._format_shap_explanation(
                top_features,
                shap_values_for_prediction,
                feature_names,
                feature_values
            )
            
            print(f"\n✅ Explanation: {explanation}")
            print("="*60 + "\n")
            
            return top_features, explanation
            
        except Exception as e:
            print(f"\n❌ SHAP ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            print("\n⚠️  Falling back to coefficient-based explanation...")
            print("="*60 + "\n")
            
            return self._explain_svm_with_coefficients(model, features_transformed, feature_names, feature_values)
    
    def _format_feature_importance_explanation(self, top_features, feature_values, feature_names):
        """Format feature importance into natural language"""
        
        if not top_features:
            return "Prediction based on multiple factors."
        
        explanations = []
        
        for feature in top_features:
            name = feature['name']
            value = feature['value']
            importance = feature['impact']
            
            # Get readable name
            readable_name = self.FEATURE_NAMES.get(name, name.replace('_', ' ').title())
            
            # Format value based on feature type
            if 'ratio' in name.lower() or 'equity' in name.lower():
                value_str = f"{value:.2f}"
            elif 'growth' in name.lower() or 'trend' in name.lower() or 'cagr' in name.lower():
                value_str = f"{value:.1f}%"
            else:
                value_str = f"{value:.1f}"
            
            # Create explanation
            explanations.append(
                f"{readable_name} ({value_str}) is a key factor with {importance*100:.1f}% importance"
            )
        
        return ". ".join(explanations) + "."
    
    def _format_shap_explanation(self, top_features, shap_values, feature_names, feature_values):
        """Format SHAP values into natural language"""
        
        if not top_features:
            return "Prediction based on multiple factors."
        
        explanations = []
        
        for i, feature in enumerate(top_features):
            name = feature['name']
            value = feature['value']
            
            # Get SHAP value for this feature
            feature_idx = list(feature_names).index(name)
            shap_value = shap_values[feature_idx]
            
            # Get readable name
            readable_name = self.FEATURE_NAMES.get(name, name.replace('_', ' ').title())
            
            # Format value
            if 'ratio' in name.lower() or 'equity' in name.lower():
                value_str = f"{value:.2f}"
            elif 'growth' in name.lower() or 'trend' in name.lower() or 'cagr' in name.lower():
                value_str = f"{value:.1f}%"
            else:
                value_str = f"{value:.1f}"
            
            # Determine direction
            direction = "positively" if shap_value > 0 else "negatively"
            
            # Create explanation
            explanations.append(
                f"{readable_name} ({value_str}) contributes {direction} with impact of {abs(shap_value):.3f}"
            )
        
        return ". ".join(explanations) + "."
    
    def _format_coefficient_explanation(self, top_features, feature_values, feature_names):
        """Format coefficient-based explanation into natural language"""
        
        if not top_features:
            return "Prediction based on multiple growth factors."
        
        explanations = []
        
        for feature in top_features:
            name = feature['name']
            value = feature['value']
            impact = feature['impact']
            
            # Get readable name
            readable_name = self.FEATURE_NAMES.get(name, name.replace('_', ' ').title())
            
            # Format value
            if 'ratio' in name.lower() or 'equity' in name.lower():
                value_str = f"{value:.2f}"
            elif 'growth' in name.lower() or 'trend' in name.lower() or 'cagr' in name.lower():
                value_str = f"{value:.1f}%"
            else:
                value_str = f"{value:.1f}"
            
            # Create explanation
            explanations.append(
                f"{readable_name} ({value_str}) is a significant factor with impact score of {impact:.3f}"
            )
        
        return ". ".join(explanations) + "."
    
    def _explain_svm_with_coefficients(self, model, features_transformed, feature_names, feature_values):
        """
        Fallback for Model 3 (SVM): Use model coefficients
        """
        try:
            # SVM has coef_ attribute for linear kernels
            if hasattr(model, 'coef_'):
                coefficients = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
                
                # Multiply coefficients by feature values for impact
                impacts = np.abs(coefficients * features_transformed[0])
                
                # Get top 3
                top_indices = np.argsort(impacts)[-3:][::-1]
                
                top_features = []
                for idx in top_indices:
                    top_features.append({
                        'name': feature_names[idx],
                        'value': float(feature_values[idx]),
                        'impact': float(impacts[idx])
                    })
                
                # Generate explanation
                explanation = self._format_coefficient_explanation(top_features, feature_values, feature_names)
                
                return top_features, explanation
            
            # Ultimate fallback: Use feature values
            else:
                abs_features = np.abs(features_transformed[0])
                top_indices = np.argsort(abs_features)[-3:][::-1]
                
                top_features = []
                for idx in top_indices:
                    top_features.append({
                        'name': feature_names[idx],
                        'value': float(feature_values[idx]),
                        'impact': float(abs_features[idx])
                    })
                
                explanation = "Prediction based on key growth metrics. " + \
                            ", ".join([f"{f['name'].replace('_', ' ')}" for f in top_features[:3]])
                
                return top_features, explanation
                
        except Exception as e:
            print(f"⚠️  Fallback explanation error: {e}")
            return [], "Unable to generate detailed explanation."
    
    @staticmethod
    def generate_ensemble_reasoning(val_pred, health_pred, growth_pred, final_rec, top_features):
        """Generate overall ensemble reasoning"""
        
        # Map predictions to descriptors
        val_desc = {
            "UNDERVALUED": "undervalued",
            "FAIR": "fairly valued",
            "OVERVALUED": "overvalued"
        }.get(val_pred, "valued")
        
        health_desc = {
            "EXCELLENT": "excellent financial health",
            "FAIR": "fair financial health",
            "POOR": "concerning financial health"
        }.get(health_pred, "financial health")
        
        growth_desc = {
            "STRONG_GROWTH": "strong growth trajectory",
            "MODERATE_GROWTH": "moderate growth potential",
            "WEAK_GROWTH": "weak growth signals",
            "DECLINING": "declining performance"
        }.get(growth_pred, "growth")
        
        # Build reasoning
        if final_rec == "BUY":
            reasoning = f"All three models indicate positive signals. The stock is {val_desc} with {health_desc} and {growth_desc}."
        elif final_rec == "SELL":
            reasoning = f"Multiple models show concerning signals. The stock is {val_desc} with {health_desc} and {growth_desc}."
        else:  # HOLD
            reasoning = f"Mixed signals from the models. The stock is {val_desc} with {health_desc} and {growth_desc}. Further analysis recommended."
        
        # Add top contributing factor if available
        if top_features and len(top_features) > 0:
            top_feature = top_features[0]
            feature_name = ExplanationService.FEATURE_NAMES.get(
                top_feature['name'], 
                top_feature['name'].replace('_', ' ').title()
            )
            reasoning += f" {feature_name} is the most significant factor influencing this recommendation."
        
        return reasoning