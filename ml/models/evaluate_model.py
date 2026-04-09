#!/usr/bin/env python3
"""
Model Evaluation and Prediction Functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pickle

from ml.utils.ml_utils import MLUtils
from app import create_app, db
from app.models.sales_transaction import SalesTransaction
from app.models.product import Product

class ModelEvaluator:
    def __init__(self, model_path='ml/models/lstm_forecaster.h5'):
        self.model = None
        self.scaler = None
        self.metadata = None
        self.load_model_and_data(model_path)
    
    def load_model_and_data(self, model_path):
        """Load trained model and preprocessing data"""
        try:
            # Load model
            self.model = tf.keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
            
            # Load scaler and metadata
            with open('ml/data/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            
            with open('ml/data/metadata.pkl', 'rb') as f:
                self.metadata = pickle.load(f)
            
            print("Preprocessing data loaded successfully")
            
        except Exception as e:
            print(f"Error loading model or data: {e}")
            raise
    
    def predict_demand(self, product_id, days_ahead=7):
        """Predict demand for a specific product"""
        # Get recent sales data for the product
        recent_data = self._get_recent_product_data(product_id)
        
        if recent_data is None or len(recent_data) < self.metadata['lookback_days']:
            return None, "Insufficient historical data"
        
        # Prepare features
        features = self._prepare_features(recent_data)
        
        # Create sequence
        sequence = features[-self.metadata['lookback_days']:].reshape(1, self.metadata['lookback_days'], -1)
        
        # Make prediction
        prediction = self.model.predict(sequence, verbose=0)[0]
        
        # Ensure non-negative predictions
        prediction = np.maximum(prediction, 0)
        
        # Calculate confidence score (simplified)
        confidence = self._calculate_confidence(recent_data, prediction)
        
        return prediction[:days_ahead], confidence
    
    def _get_recent_product_data(self, product_id, days=60):
        """Get recent sales data for a product"""
        app = create_app()
        
        with app.app_context():
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Query sales data
            query = db.session.query(
                SalesTransaction.sale_date,
                SalesTransaction.quantity_sold
            ).filter(
                SalesTransaction.product_id == product_id,
                SalesTransaction.sale_date >= start_date,
                SalesTransaction.sale_date <= end_date
            ).order_by(SalesTransaction.sale_date)
            
            df = pd.read_sql(query.statement, db.engine)
            
            if df.empty:
                return None
            
            # Create complete date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            complete_df = pd.DataFrame({'sale_date': date_range})
            
            # Merge with actual data
            merged = complete_df.merge(df, on='sale_date', how='left')
            merged['quantity_sold'] = merged['quantity_sold'].fillna(0)
            
            return merged
    
    def _prepare_features(self, df):
        """Prepare features for prediction (simplified version)"""
        df = df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Basic time features
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['month'] = df['sale_date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Lag features
        for lag in [1, 3, 7]:
            df[f'lag_{lag}'] = df['quantity_sold'].shift(lag)
        
        # Rolling features
        for window in [3, 7]:
            df[f'rolling_mean_{window}'] = df['quantity_sold'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['quantity_sold'].rolling(window).std()
        
        # Fill NaN values
        df = df.fillna(method='ffill').fillna(0)
        
        # Select feature columns (match training features)
        feature_cols = [col for col in df.columns if col not in ['sale_date', 'quantity_sold']]
        features = df[feature_cols].values
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        return features_scaled
    
    def _calculate_confidence(self, recent_data, prediction):
        """Calculate prediction confidence score"""
        # Simple confidence based on recent data variability
        recent_sales = recent_data['quantity_sold'].values[-14:]  # Last 2 weeks
        
        if len(recent_sales) == 0:
            return 0.5
        
        # Calculate coefficient of variation
        mean_sales = np.mean(recent_sales)
        std_sales = np.std(recent_sales)
        
        if mean_sales == 0:
            cv = 1.0
        else:
            cv = std_sales / mean_sales
        
        # Convert to confidence (lower variability = higher confidence)
        confidence = max(0.1, min(0.9, 1.0 - cv))
        
        return confidence
    
    def batch_predict(self, product_ids, days_ahead=7):
        """Predict demand for multiple products"""
        results = {}
        
        for product_id in product_ids:
            try:
                prediction, confidence = self.predict_demand(product_id, days_ahead)
                if prediction is not None:
                    results[product_id] = {
                        'prediction': prediction.tolist(),
                        'confidence': confidence
                    }
                else:
                    results[product_id] = {
                        'error': 'Insufficient data'
                    }
            except Exception as e:
                results[product_id] = {
                    'error': str(e)
                }
        
        return results
    
    def evaluate_model_performance(self):
        """Evaluate model performance on test data"""
        # Load test data
        data = MLUtils.load_processed_data()
        X_test, y_test = data['test']
        
        # Make predictions
        y_pred = self.model.predict(X_test, verbose=0)
        
        # Calculate metrics
        metrics = MLUtils.calculate_metrics(y_test, y_pred)
        
        # Plot results
        MLUtils.plot_predictions(y_test, y_pred, "Model Performance Evaluation")
        
        return metrics
    
    def forecast_accuracy_analysis(self, product_id, test_days=30):
        """Analyze forecast accuracy for a specific product"""
        # Get historical data
        historical_data = self._get_recent_product_data(product_id, days=90)
        
        if historical_data is None or len(historical_data) < 60:
            return None, "Insufficient data for analysis"
        
        # Split data for backtesting
        train_end = len(historical_data) - test_days
        train_data = historical_data[:train_end]
        test_data = historical_data[train_end:]
        
        predictions = []
        actuals = test_data['quantity_sold'].values
        
        # Rolling forecast
        for i in range(len(test_data) - 7):
            # Use data up to current point
            current_data = pd.concat([train_data, test_data[:i]])
            
            # Prepare features and predict
            features = self._prepare_features(current_data)
            if len(features) >= self.metadata['lookback_days']:
                sequence = features[-self.metadata['lookback_days']:].reshape(1, -1, features.shape[1])
                pred = self.model.predict(sequence, verbose=0)[0]
                predictions.append(pred[0])  # Next day prediction
            else:
                predictions.append(0)
        
        # Calculate accuracy metrics
        if len(predictions) > 0:
            predictions = np.array(predictions)
            test_actuals = actuals[:len(predictions)]
            metrics = MLUtils.calculate_metrics(test_actuals, predictions)
            
            # Plot comparison
            dates = pd.date_range(start=test_data.iloc[0]['sale_date'], periods=len(predictions))
            MLUtils.plot_forecast_comparison(
                test_actuals, predictions, dates,
                f"Product {product_id} Forecast Accuracy"
            )
            
            return metrics, predictions
        
        return None, "Could not generate predictions"

def run_model_evaluation():
    """Run comprehensive model evaluation"""
    print("Starting model evaluation...")
    
    try:
        evaluator = ModelEvaluator()
        
        # Overall model performance
        print("\n1. Overall Model Performance:")
        metrics = evaluator.evaluate_model_performance()
        print(f"Test MAE: {metrics['mae']:.4f}")
        print(f"Test RMSE: {metrics['rmse']:.4f}")
        print(f"Test MAPE: {metrics['mape']:.2f}%")
        
        # Test prediction for a specific product
        print("\n2. Sample Product Prediction:")
        prediction, confidence = evaluator.predict_demand(product_id=1, days_ahead=7)
        if prediction is not None:
            print(f"7-day forecast: {prediction}")
            print(f"Confidence: {confidence:.2f}")
        else:
            print("Could not generate prediction")
        
        # Batch prediction example
        print("\n3. Batch Prediction (Products 1-5):")
        batch_results = evaluator.batch_predict([1, 2, 3, 4, 5])
        for product_id, result in batch_results.items():
            if 'prediction' in result:
                print(f"Product {product_id}: {result['prediction'][:3]}... (confidence: {result['confidence']:.2f})")
            else:
                print(f"Product {product_id}: {result.get('error', 'Unknown error')}")
        
        print("\nModel evaluation completed!")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")

def create_prediction_api():
    """Create a simple prediction function for API integration"""
    
    def predict_product_demand(product_id, days_ahead=7):
        """API-friendly prediction function"""
        try:
            evaluator = ModelEvaluator()
            prediction, confidence = evaluator.predict_demand(product_id, days_ahead)
            
            if prediction is not None:
                return {
                    'success': True,
                    'product_id': product_id,
                    'forecast': prediction.tolist(),
                    'confidence_score': float(confidence),
                    'forecast_days': days_ahead,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Insufficient historical data for prediction'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    return predict_product_demand

if __name__ == '__main__':
    # Run evaluation
    run_model_evaluation()
    
    # Test API function
    print("\n" + "="*50)
    print("Testing API Integration:")
    predict_func = create_prediction_api()
    result = predict_func(1, 7)
    print(f"API Result: {result}")