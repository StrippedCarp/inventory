#!/usr/bin/env python3
"""
Simplified ML Model Training using Scikit-Learn
Alternative to LSTM for demand forecasting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import pickle
from datetime import datetime, timedelta

class SimpleForecastModel:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        # Initialize model based on type
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        elif model_type == 'gradient_boost':
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == 'linear':
            self.model = LinearRegression()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def prepare_ml_data(self, sequences, targets):
        """Convert sequence data to ML format"""
        # Flatten sequences for traditional ML models
        n_samples, n_timesteps, n_features = sequences.shape
        X_flat = sequences.reshape(n_samples, n_timesteps * n_features)
        
        # Use mean of target sequence as single target
        y_flat = np.mean(targets, axis=1)
        
        return X_flat, y_flat
    
    def train(self, train_data, val_data):
        """Train the model"""
        X_train_seq, y_train_seq = train_data
        X_val_seq, y_val_seq = val_data
        
        # Convert to ML format
        X_train, y_train = self.prepare_ml_data(X_train_seq, y_train_seq)
        X_val, y_val = self.prepare_ml_data(X_val_seq, y_val_seq)
        
        print(f"Training {self.model_type} model...")
        print(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate on validation set
        val_pred = self.model.predict(X_val)
        val_mae = mean_absolute_error(y_val, val_pred)
        val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
        
        print(f"Validation MAE: {val_mae:.4f}")
        print(f"Validation RMSE: {val_rmse:.4f}")
        
        return {'val_mae': val_mae, 'val_rmse': val_rmse}
    
    def predict(self, X_seq):
        """Make predictions"""
        X_flat, _ = self.prepare_ml_data(X_seq, np.zeros((X_seq.shape[0], 7)))
        pred_flat = self.model.predict(X_flat)
        
        # Expand single prediction to 7-day forecast
        pred_expanded = np.repeat(pred_flat.reshape(-1, 1), 7, axis=1)
        return pred_expanded
    
    def evaluate(self, test_data):
        """Evaluate model on test data"""
        X_test_seq, y_test_seq = test_data
        
        # Make predictions
        y_pred = self.predict(X_test_seq)
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_test_seq, y_pred)
        
        print(f"Test Results ({self.model_type}):")
        print(f"- MAE: {metrics['mae']:.4f}")
        print(f"- RMSE: {metrics['rmse']:.4f}")
        print(f"- MAPE: {metrics['mape']:.2f}%")
        
        return y_pred, metrics
    
    def calculate_metrics(self, y_true, y_pred):
        """Calculate regression metrics"""
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        mask = np.isfinite(y_true_flat) & np.isfinite(y_pred_flat)
        y_true_clean = y_true_flat[mask]
        y_pred_clean = y_pred_flat[mask]
        
        if len(y_true_clean) == 0:
            return {'mae': np.nan, 'rmse': np.nan, 'mape': np.nan}
        
        mae = mean_absolute_error(y_true_clean, y_pred_clean)
        rmse = np.sqrt(mean_squared_error(y_true_clean, y_pred_clean))
        mape = np.mean(np.abs((y_true_clean - y_pred_clean) / np.maximum(y_true_clean, 1e-8))) * 100
        
        return {'mae': mae, 'rmse': rmse, 'mape': mape}
    
    def save_model(self, filepath='ml/models/simple_forecaster.pkl'):
        """Save the trained model"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='ml/models/simple_forecaster.pkl'):
        """Load a trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        
        print(f"Model loaded from {filepath}")

def load_processed_data():
    """Load preprocessed data"""
    try:
        train_data = np.load('ml/data/train_data.npz')
        val_data = np.load('ml/data/val_data.npz')
        test_data = np.load('ml/data/test_data.npz')
        
        with open('ml/data/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        with open('ml/data/metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        
        return {
            'train': (train_data['X'], train_data['y']),
            'val': (val_data['X'], val_data['y']),
            'test': (test_data['X'], test_data['y']),
            'scaler': scaler,
            'metadata': metadata
        }
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Processed data not found. Run preprocess_simple.py first. Error: {e}")

def calculate_metrics(y_true, y_pred):
    """Calculate regression metrics"""
    y_true_flat = y_true.flatten()
    y_pred_flat = y_pred.flatten()
    
    mask = np.isfinite(y_true_flat) & np.isfinite(y_pred_flat)
    y_true_clean = y_true_flat[mask]
    y_pred_clean = y_pred_flat[mask]
    
    if len(y_true_clean) == 0:
        return {'mae': np.nan, 'rmse': np.nan, 'mape': np.nan}
    
    mae = mean_absolute_error(y_true_clean, y_pred_clean)
    rmse = np.sqrt(mean_squared_error(y_true_clean, y_pred_clean))
    mape = np.mean(np.abs((y_true_clean - y_pred_clean) / np.maximum(y_true_clean, 1e-8))) * 100
    
    return {'mae': mae, 'rmse': rmse, 'mape': mape}

def train_simple_models():
    """Train multiple simple models and compare"""
    print("Training Simple ML Models for Demand Forecasting...")
    
    # Load processed data
    try:
        data = load_processed_data()
    except FileNotFoundError:
        print("Processed data not found. Please run preprocess_simple.py first.")
        return None
    
    train_data = data['train']
    val_data = data['val']
    test_data = data['test']
    
    # Model types to try
    model_types = ['random_forest', 'gradient_boost', 'linear']
    results = {}
    
    for model_type in model_types:
        print(f"\n{'='*50}")
        print(f"Training {model_type.upper()} Model")
        print(f"{'='*50}")
        
        # Initialize and train model
        model = SimpleForecastModel(model_type)
        train_metrics = model.train(train_data, val_data)
        
        # Evaluate on test data
        y_pred, test_metrics = model.evaluate(test_data)
        
        # Save model
        model.save_model(f'ml/models/{model_type}_forecaster.pkl')
        
        # Store results
        results[model_type] = {
            'model': model,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'predictions': y_pred
        }
        
        # Plot predictions
        plt.figure(figsize=(10, 6))
        y_test_flat = test_data[1].flatten()
        y_pred_flat = y_pred.flatten()
        plt.scatter(y_test_flat, y_pred_flat, alpha=0.6)
        plt.plot([y_test_flat.min(), y_test_flat.max()], [y_test_flat.min(), y_test_flat.max()], 'r--')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title(f'{model_type.title()} Predictions vs Actual')
        plt.savefig(f'ml/models/{model_type}_predictions.png')
        plt.close()
    
    # Compare models
    print(f"\n{'='*50}")
    print("MODEL COMPARISON")
    print(f"{'='*50}")
    print(f"{'Model':<15} {'Test MAE':<10} {'Test RMSE':<11} {'Test MAPE':<10}")
    print("-" * 50)
    
    best_model = None
    best_mae = float('inf')
    
    for model_type, result in results.items():
        metrics = result['test_metrics']
        print(f"{model_type:<15} {metrics['mae']:<10.4f} {metrics['rmse']:<11.4f} {metrics['mape']:<10.2f}%")
        
        if metrics['mae'] < best_mae:
            best_mae = metrics['mae']
            best_model = model_type
    
    print(f"\nBest model: {best_model} (MAE: {best_mae:.4f})")
    
    # Save best model as default
    if best_model:
        results[best_model]['model'].save_model('ml/models/best_forecaster.pkl')
    
    return results

def create_baseline_comparison(data):
    """Create baseline models for comparison"""
    print("Creating baseline models...")
    
    X_test, y_test = data['test']
    
    baselines = {}
    
    # Naive forecast (repeat last value)
    naive_pred = np.repeat(X_test[:, -1, 0:1], y_test.shape[1], axis=1)
    baselines['naive'] = calculate_metrics(y_test, naive_pred)
    
    # Moving average (7-day)
    ma_pred = np.mean(X_test[:, -7:, 0], axis=1, keepdims=True)
    ma_pred = np.repeat(ma_pred, y_test.shape[1], axis=1)
    baselines['moving_average'] = calculate_metrics(y_test, ma_pred)
    
    print("\nBaseline Model Performance:")
    print(f"{'Model':<15} {'MAE':<10} {'RMSE':<11} {'MAPE':<10}")
    print("-" * 50)
    for name, metrics in baselines.items():
        print(f"{name:<15} {metrics['mae']:<10.4f} {metrics['rmse']:<11.4f} {metrics['mape']:<10.2f}%")
    
    return baselines

class SimplePredictor:
    """Simple predictor for API integration"""
    
    def __init__(self, model_path='ml/models/best_forecaster.pkl'):
        self.model = SimpleForecastModel()
        self.model.load_model(model_path)
        
        # Load preprocessing data
        with open('ml/data/scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open('ml/data/metadata.pkl', 'rb') as f:
            self.metadata = pickle.load(f)
    
    def predict_demand(self, product_id, days_ahead=7):
        """Predict demand for a product (simplified)"""
        try:
            # This is a simplified version - in practice, you'd fetch real data
            # For now, create dummy features
            n_features = self.metadata['n_features']
            lookback_days = self.metadata['lookback_days']
            
            # Create dummy sequence (in practice, fetch from database)
            dummy_sequence = np.random.randn(1, lookback_days, n_features)
            
            # Make prediction
            prediction = self.model.predict(dummy_sequence)[0]
            
            # Calculate simple confidence
            confidence = 0.75  # Simplified confidence score
            
            return prediction[:days_ahead], confidence
            
        except Exception as e:
            return None, str(e)

def main():
    """Main training function"""
    print("Simple ML Model Training Pipeline")
    print("=" * 50)
    
    # Create output directories
    os.makedirs('ml/models', exist_ok=True)
    os.makedirs('ml/results', exist_ok=True)
    
    # Train models
    results = train_simple_models()
    
    if results:
        # Load data for baseline comparison
        data = load_processed_data()
        
        # Create baselines
        baselines = create_baseline_comparison(data)
        
        # Save all results
        with open('ml/results/model_comparison.pkl', 'wb') as f:
            pickle.dump({'models': results, 'baselines': baselines}, f)
        
        print(f"\nTraining completed successfully!")
        print("Check ml/models/ for saved models and ml/results/ for comparisons.")
    
    return results

if __name__ == '__main__':
    results = main()