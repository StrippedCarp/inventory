#!/usr/bin/env python3
"""
LSTM Model Training for Demand Forecasting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2
import matplotlib.pyplot as plt
import pickle
from datetime import datetime

from ml.utils.ml_utils import MLUtils, DataValidator

class LSTMForecaster:
    def __init__(self, lookback_days=30, forecast_days=7):
        self.lookback_days = lookback_days
        self.forecast_days = forecast_days
        self.model = None
        self.history = None
        
    def build_model(self, n_features):
        """Build LSTM model architecture"""
        model = Sequential([
            # First LSTM layer
            LSTM(128, return_sequences=True, input_shape=(self.lookback_days, n_features),
                 kernel_regularizer=l2(0.001), recurrent_regularizer=l2(0.001)),
            BatchNormalization(),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(64, return_sequences=False,
                 kernel_regularizer=l2(0.001), recurrent_regularizer=l2(0.001)),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers
            Dense(32, activation='relu', kernel_regularizer=l2(0.001)),
            Dropout(0.1),
            
            # Output layer
            Dense(self.forecast_days, activation='linear')
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def create_callbacks(self, model_save_path='ml/models/lstm_model.h5'):
        """Create training callbacks"""
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=model_save_path,
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        return callbacks
    
    def train(self, train_data, val_data, epochs=50, batch_size=32):
        """Train the LSTM model"""
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        print(f"Training LSTM model...")
        print(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
        print(f"Validation data shape: X={X_val.shape}, y={y_val.shape}")
        
        # Build model if not already built
        if self.model is None:
            self.build_model(X_train.shape[2])
        
        # Print model summary
        print("\nModel Architecture:")
        self.model.summary()
        
        # Create callbacks
        os.makedirs('ml/models', exist_ok=True)
        callbacks = self.create_callbacks()
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        print("Training completed!")
        return self.history
    
    def evaluate(self, test_data):
        """Evaluate model on test data"""
        X_test, y_test = test_data
        
        print("Evaluating model on test data...")
        
        # Make predictions
        y_pred = self.model.predict(X_test, verbose=0)
        
        # Calculate metrics
        metrics = MLUtils.calculate_metrics(y_test, y_pred)
        
        print(f"Test Results:")
        print(f"- MAE: {metrics['mae']:.4f}")
        print(f"- RMSE: {metrics['rmse']:.4f}")
        print(f"- MAPE: {metrics['mape']:.2f}%")
        
        return y_pred, metrics
    
    def predict(self, X):
        """Make predictions on new data"""
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        return self.model.predict(X, verbose=0)
    
    def save_model(self, filepath='ml/models/lstm_forecaster.h5'):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save(filepath)
        
        # Save model metadata
        metadata = {
            'lookback_days': self.lookback_days,
            'forecast_days': self.forecast_days,
            'model_type': 'LSTM',
            'trained_at': datetime.now().isoformat()
        }
        
        with open(filepath.replace('.h5', '_metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='ml/models/lstm_forecaster.h5'):
        """Load a trained model"""
        self.model = tf.keras.models.load_model(filepath)
        
        # Load metadata if available
        metadata_path = filepath.replace('.h5', '_metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            self.lookback_days = metadata.get('lookback_days', 30)
            self.forecast_days = metadata.get('forecast_days', 7)
        
        print(f"Model loaded from {filepath}")

def train_lstm_model():
    """Main training function"""
    print("Starting LSTM model training...")
    
    # Load processed data
    try:
        data = MLUtils.load_processed_data()
    except FileNotFoundError:
        print("Processed data not found. Please run preprocess_data.py first.")
        return None
    
    # Extract data
    train_data = data['train']
    val_data = data['val']
    test_data = data['test']
    metadata = data['metadata']
    
    # Validate data
    print("Validating data...")
    for name, (X, y) in [('Training', train_data), ('Validation', val_data), ('Test', test_data)]:
        DataValidator.print_data_summary(X, y, name)
    
    # Initialize forecaster
    forecaster = LSTMForecaster(
        lookback_days=metadata['lookback_days'],
        forecast_days=metadata['forecast_days']
    )
    
    # Train model
    history = forecaster.train(
        train_data=train_data,
        val_data=val_data,
        epochs=50,
        batch_size=32
    )
    
    # Evaluate on test data
    y_pred, test_metrics = forecaster.evaluate(test_data)
    
    # Save model
    forecaster.save_model()
    
    # Plot training history
    MLUtils.plot_training_history(history, 'ml/models/training_history.png')
    
    # Plot predictions vs actual
    MLUtils.plot_predictions(
        test_data[1], y_pred, 
        title="LSTM Test Predictions vs Actual",
        save_path='ml/models/test_predictions.png'
    )
    
    # Save results
    MLUtils.save_model_results('lstm', test_metrics, y_pred)
    
    print(f"\nTraining Summary:")
    print(f"- Best validation loss: {min(history.history['val_loss']):.4f}")
    print(f"- Test MAE: {test_metrics['mae']:.4f}")
    print(f"- Test RMSE: {test_metrics['rmse']:.4f}")
    print(f"- Test MAPE: {test_metrics['mape']:.2f}%")
    
    return forecaster, test_metrics

def create_baseline_models(data):
    """Create simple baseline models for comparison"""
    train_data, val_data, test_data = data['train'], data['val'], data['test']
    X_test, y_test = test_data
    
    baselines = {}
    
    # Naive forecast (last value)
    naive_pred = np.repeat(X_test[:, -1, 0:1], y_test.shape[1], axis=1)
    baselines['naive'] = MLUtils.calculate_metrics(y_test, naive_pred)
    
    # Moving average forecast
    ma_pred = np.mean(X_test[:, -7:, 0], axis=1, keepdims=True)
    ma_pred = np.repeat(ma_pred, y_test.shape[1], axis=1)
    baselines['moving_average'] = MLUtils.calculate_metrics(y_test, ma_pred)
    
    # Seasonal naive (same day last week)
    if X_test.shape[1] >= 7:
        seasonal_pred = np.repeat(X_test[:, -7, 0:1], y_test.shape[1], axis=1)
        baselines['seasonal_naive'] = MLUtils.calculate_metrics(y_test, seasonal_pred)
    
    print("\nBaseline Model Performance:")
    for name, metrics in baselines.items():
        print(f"{name.title()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, MAPE={metrics['mape']:.2f}%")
    
    return baselines

def hyperparameter_tuning():
    """Simple hyperparameter tuning"""
    print("Starting hyperparameter tuning...")
    
    # Load data
    data = MLUtils.load_processed_data()
    train_data, val_data = data['train'], data['val']
    
    # Hyperparameter combinations to try
    param_combinations = [
        {'lstm1': 64, 'lstm2': 32, 'dense': 16, 'dropout': 0.1, 'lr': 0.001},
        {'lstm1': 128, 'lstm2': 64, 'dense': 32, 'dropout': 0.2, 'lr': 0.001},
        {'lstm1': 256, 'lstm2': 128, 'dense': 64, 'dropout': 0.3, 'lr': 0.0005},
    ]
    
    best_score = float('inf')
    best_params = None
    results = []
    
    for i, params in enumerate(param_combinations):
        print(f"\nTrying combination {i+1}/{len(param_combinations)}: {params}")
        
        # Build custom model
        model = Sequential([
            LSTM(params['lstm1'], return_sequences=True, input_shape=(30, train_data[0].shape[2])),
            Dropout(params['dropout']),
            LSTM(params['lstm2'], return_sequences=False),
            Dropout(params['dropout']),
            Dense(params['dense'], activation='relu'),
            Dense(7, activation='linear')
        ])
        
        model.compile(optimizer=Adam(learning_rate=params['lr']), loss='mse', metrics=['mae'])
        
        # Train with early stopping
        history = model.fit(
            train_data[0], train_data[1],
            validation_data=val_data,
            epochs=20,  # Reduced for tuning
            batch_size=32,
            callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
            verbose=0
        )
        
        # Get best validation score
        best_val_loss = min(history.history['val_loss'])
        results.append({'params': params, 'val_loss': best_val_loss})
        
        if best_val_loss < best_score:
            best_score = best_val_loss
            best_params = params
        
        print(f"Validation loss: {best_val_loss:.4f}")
    
    print(f"\nBest parameters: {best_params}")
    print(f"Best validation loss: {best_score:.4f}")
    
    return best_params, results

if __name__ == '__main__':
    # Set random seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Train main model
    forecaster, metrics = train_lstm_model()
    
    # Create baseline comparisons
    data = MLUtils.load_processed_data()
    baselines = create_baseline_models(data)
    
    print("\nModel training completed successfully!")
    print("Check ml/models/ for saved model and visualizations.")