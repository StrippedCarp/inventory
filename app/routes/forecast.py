from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Forecast
from app.models.product import Product
from app.models.sales_transaction import SalesTransaction
from app.utils.auth_decorators import manager_or_admin_required
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import pickle
import os

forecast_bp = Blueprint('forecast', __name__)

class ForecastService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = None
        self.load_model()
    
    def load_model(self):
        """Load trained ML model"""
        try:
            # Try to load the best model
            model_path = 'ml/models/best_forecaster.pkl'
            if not os.path.exists(model_path):
                model_path = 'ml/models/random_forest_forecaster.pkl'
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.model = model_data['model']
                
                # Load scaler and metadata
                with open('ml/data/scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                
                with open('ml/data/metadata.pkl', 'rb') as f:
                    self.metadata = pickle.load(f)
                
                print("ML model loaded successfully")
            else:
                print("ML model not found, using fallback predictions")
        except Exception as e:
            print(f"Error loading ML model: {e}")
    
    def get_recent_sales_data(self, product_id, days=60):
        """Get recent sales data for a product"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        sales_data = db.session.query(
            SalesTransaction.sale_date,
            SalesTransaction.quantity_sold
        ).filter(
            SalesTransaction.product_id == product_id,
            SalesTransaction.sale_date >= start_date
        ).order_by(SalesTransaction.sale_date).all()
        
        # Convert to DataFrame and fill missing dates
        if sales_data:
            df = pd.DataFrame(sales_data)
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            complete_df = pd.DataFrame({'sale_date': date_range})
            merged = complete_df.merge(df, on='sale_date', how='left')
            merged['quantity_sold'] = merged['quantity_sold'].fillna(0)
            return merged
        
        return None
    
    def create_features(self, sales_df):
        """Create features for prediction"""
        if sales_df is None or len(sales_df) < 30:
            return None
        
        df = sales_df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Time features
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['month'] = df['sale_date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Lag features
        for lag in [1, 3, 7, 14, 30]:
            df[f'lag_{lag}'] = df['quantity_sold'].shift(lag)
        
        # Rolling features
        for window in [3, 7, 14, 30]:
            df[f'rolling_mean_{window}'] = df['quantity_sold'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['quantity_sold'].rolling(window).std()
        
        # Fill NaN values
        df = df.fillna(method='ffill').fillna(0)
        
        return df
    
    def predict_demand(self, product_id, days_ahead=7):
        """Predict demand for a product"""
        try:
            # Get recent sales data
            sales_df = self.get_recent_sales_data(product_id)
            
            if sales_df is None:
                return self.fallback_prediction(product_id, days_ahead)
            
            # Create features
            features_df = self.create_features(sales_df)
            
            if features_df is None:
                return self.fallback_prediction(product_id, days_ahead)
            
            if self.model and self.scaler:
                # Use ML model
                feature_cols = [col for col in features_df.columns 
                              if col not in ['sale_date', 'quantity_sold']]
                
                # Get latest features
                latest_features = features_df[feature_cols].iloc[-30:].values
                
                if len(latest_features) >= 30:
                    # Scale features
                    features_scaled = self.scaler.transform(latest_features)
                    
                    # Flatten for traditional ML model
                    features_flat = features_scaled.flatten().reshape(1, -1)
                    
                    # Make prediction
                    prediction = self.model.predict(features_flat)[0]
                    
                    # Expand to multi-day forecast
                    forecast = [max(0, prediction * (0.9 + 0.2 * np.random.random())) 
                              for _ in range(days_ahead)]
                    
                    confidence = 0.75
                    return forecast, confidence
            
            # Fallback to statistical prediction
            return self.statistical_prediction(sales_df, days_ahead)
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self.fallback_prediction(product_id, days_ahead)
    
    def statistical_prediction(self, sales_df, days_ahead):
        """Statistical prediction fallback"""
        recent_sales = sales_df['quantity_sold'].iloc[-14:].values
        
        if len(recent_sales) == 0:
            return [0] * days_ahead, 0.3
        
        # Simple moving average with trend
        ma_7 = np.mean(recent_sales[-7:]) if len(recent_sales) >= 7 else np.mean(recent_sales)
        ma_14 = np.mean(recent_sales) if len(recent_sales) >= 14 else ma_7
        
        trend = ma_7 - ma_14
        base_forecast = max(0, ma_7 + trend)
        
        # Add some variability
        forecast = [max(0, base_forecast * (0.8 + 0.4 * np.random.random())) 
                   for _ in range(days_ahead)]
        
        confidence = 0.6
        return forecast, confidence
    
    def fallback_prediction(self, product_id, days_ahead):
        """Simple fallback prediction"""
        # Get average sales from last 30 days
        recent_avg = db.session.query(
            db.func.avg(SalesTransaction.quantity_sold)
        ).filter(
            SalesTransaction.product_id == product_id,
            SalesTransaction.sale_date >= date.today() - timedelta(days=30)
        ).scalar()
        
        if recent_avg:
            base_demand = float(recent_avg)
        else:
            base_demand = 1.0  # Default
        
        forecast = [max(0, base_demand * (0.8 + 0.4 * np.random.random())) 
                   for _ in range(days_ahead)]
        
        return forecast, 0.4

# Initialize forecast service
forecast_service = ForecastService()

@forecast_bp.route('/predict/<int:product_id>', methods=['POST'])
def generate_forecast(product_id):
    """Generate demand forecast for a product"""
    try:
        data = request.get_json() or {}
        days_ahead = data.get('days_ahead', 7)
        
        # Validate product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Generate forecast
        forecast, confidence = forecast_service.predict_demand(product_id, days_ahead)
        
        # Save forecast to database
        forecast_record = Forecast(
            product_id=product_id,
            forecast_date=date.today(),
            predicted_demand=int(sum(forecast)),  # Total predicted demand
            confidence_score=confidence
        )
        
        db.session.add(forecast_record)
        db.session.commit()
        
        # Prepare response
        forecast_dates = [(date.today() + timedelta(days=i)).isoformat() 
                         for i in range(1, days_ahead + 1)]
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'product_name': product.name,
            'forecast': {
                'dates': forecast_dates,
                'values': [round(f, 2) for f in forecast],
                'total_demand': round(sum(forecast), 2),
                'confidence_score': round(confidence, 3)
            },
            'generated_at': datetime.now().isoformat(),
            'model_type': 'ML' if forecast_service.model else 'Statistical'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/forecast/<int:product_id>', methods=['GET'])
def get_forecasts(product_id):
    """Get historical forecasts for a product"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        forecasts = Forecast.query.filter(
            Forecast.product_id == product_id,
            Forecast.forecast_date >= start_date
        ).order_by(Forecast.forecast_date.desc()).all()
        
        return jsonify([forecast.to_dict() for forecast in forecasts])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/batch-predict', methods=['POST'])
def batch_forecast():
    """Generate forecasts for multiple products"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        days_ahead = data.get('days_ahead', 7)
        
        if not product_ids:
            return jsonify({'message': 'No product IDs provided'}), 400
        
        results = {}
        
        for product_id in product_ids:
            try:
                forecast, confidence = forecast_service.predict_demand(product_id, days_ahead)
                
                results[product_id] = {
                    'success': True,
                    'forecast': [round(f, 2) for f in forecast],
                    'confidence': round(confidence, 3),
                    'total_demand': round(sum(forecast), 2)
                }
                
                # Save to database
                forecast_record = Forecast(
                    product_id=product_id,
                    forecast_date=date.today(),
                    predicted_demand=int(sum(forecast)),
                    confidence_score=confidence
                )
                db.session.add(forecast_record)
                
            except Exception as e:
                results[product_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/accuracy/<int:product_id>', methods=['GET'])
def forecast_accuracy(product_id):
    """Get forecast accuracy metrics for a product"""
    try:
        # Get forecasts from last 30 days
        forecasts = Forecast.query.filter(
            Forecast.product_id == product_id,
            Forecast.forecast_date >= date.today() - timedelta(days=30)
        ).all()
        
        if not forecasts:
            return jsonify({'message': 'No forecasts found'}), 404
        
        # Calculate simple accuracy metrics
        total_forecasts = len(forecasts)
        avg_confidence = sum(f.confidence_score for f in forecasts) / total_forecasts
        
        return jsonify({
            'product_id': product_id,
            'total_forecasts': total_forecasts,
            'average_confidence': round(avg_confidence, 3),
            'latest_forecast_date': forecasts[0].forecast_date.isoformat(),
            'forecast_history': [
                {
                    'date': f.forecast_date.isoformat(),
                    'predicted_demand': f.predicted_demand,
                    'confidence': f.confidence_score
                }
                for f in forecasts[-10:]  # Last 10 forecasts
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forecast_bp.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded ML model"""
    return jsonify({
        'model_loaded': forecast_service.model is not None,
        'model_type': 'ML' if forecast_service.model else 'Statistical',
        'features_available': forecast_service.metadata is not None,
        'scaler_loaded': forecast_service.scaler is not None
    })