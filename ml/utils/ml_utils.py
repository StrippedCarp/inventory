"""
Utility functions for ML pipeline
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt

class MLUtils:
    @staticmethod
    def load_processed_data():
        """Load preprocessed data and metadata"""
        try:
            # Load datasets
            train_data = np.load('ml/data/train_data.npz')
            val_data = np.load('ml/data/val_data.npz')
            test_data = np.load('ml/data/test_data.npz')
            
            # Load scaler and metadata
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
            raise FileNotFoundError(f"Processed data not found. Run preprocess_data.py first. Error: {e}")
    
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        """Calculate regression metrics"""
        # Flatten arrays if multi-dimensional
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        # Remove any NaN or infinite values
        mask = np.isfinite(y_true_flat) & np.isfinite(y_pred_flat)
        y_true_clean = y_true_flat[mask]
        y_pred_clean = y_pred_flat[mask]
        
        if len(y_true_clean) == 0:
            return {'mae': np.nan, 'rmse': np.nan, 'mape': np.nan}
        
        mae = mean_absolute_error(y_true_clean, y_pred_clean)
        rmse = np.sqrt(mean_squared_error(y_true_clean, y_pred_clean))
        
        # Calculate MAPE, handling division by zero
        mape = np.mean(np.abs((y_true_clean - y_pred_clean) / np.maximum(y_true_clean, 1e-8))) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
    
    @staticmethod
    def plot_predictions(y_true, y_pred, title="Predictions vs Actual", save_path=None):
        """Plot predictions vs actual values"""
        plt.figure(figsize=(12, 8))
        
        # Flatten arrays
        y_true_flat = y_true.flatten()
        y_pred_flat = y_pred.flatten()
        
        # Create scatter plot
        plt.scatter(y_true_flat, y_pred_flat, alpha=0.6, s=20)
        
        # Add perfect prediction line
        min_val = min(y_true_flat.min(), y_pred_flat.min())
        max_val = max(y_true_flat.max(), y_pred_flat.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add metrics as text
        metrics = MLUtils.calculate_metrics(y_true, y_pred)
        textstr = f"MAE: {metrics['mae']:.2f}\nRMSE: {metrics['rmse']:.2f}\nMAPE: {metrics['mape']:.1f}%"
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    @staticmethod
    def plot_training_history(history, save_path=None):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot training & validation loss
        ax1.plot(history.history['loss'], label='Training Loss')
        ax1.plot(history.history['val_loss'], label='Validation Loss')
        ax1.set_title('Model Loss')
        ax1.set_ylabel('Loss')
        ax1.set_xlabel('Epoch')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot training & validation metrics (if available)
        if 'mae' in history.history:
            ax2.plot(history.history['mae'], label='Training MAE')
            ax2.plot(history.history['val_mae'], label='Validation MAE')
            ax2.set_title('Model MAE')
            ax2.set_ylabel('MAE')
            ax2.set_xlabel('Epoch')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    @staticmethod
    def plot_forecast_comparison(actual, predicted, dates=None, product_name="Product", save_path=None):
        """Plot time series forecast comparison"""
        plt.figure(figsize=(15, 6))
        
        if dates is None:
            dates = range(len(actual))
        
        plt.plot(dates, actual, label='Actual', linewidth=2, marker='o', markersize=4)
        plt.plot(dates, predicted, label='Predicted', linewidth=2, marker='s', markersize=4)
        
        plt.title(f'Demand Forecast Comparison - {product_name}')
        plt.xlabel('Time')
        plt.ylabel('Demand')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add metrics
        metrics = MLUtils.calculate_metrics(actual, predicted)
        textstr = f"MAE: {metrics['mae']:.2f}\nRMSE: {metrics['rmse']:.2f}\nMAPE: {metrics['mape']:.1f}%"
        props = dict(boxstyle='round', facecolor='lightblue', alpha=0.7)
        plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    @staticmethod
    def create_sequences_for_prediction(data, lookback_days, scaler=None):
        """Create sequences for making predictions on new data"""
        if scaler is not None:
            data_scaled = scaler.transform(data)
        else:
            data_scaled = data
        
        sequences = []
        for i in range(len(data_scaled) - lookback_days + 1):
            sequences.append(data_scaled[i:i + lookback_days])
        
        return np.array(sequences)
    
    @staticmethod
    def save_model_results(model_name, metrics, predictions, save_dir='ml/results'):
        """Save model results and metrics"""
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        # Save metrics
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(f'{save_dir}/{model_name}_metrics.csv', index=False)
        
        # Save predictions
        np.save(f'{save_dir}/{model_name}_predictions.npy', predictions)
        
        print(f"Results saved to {save_dir}/{model_name}_*")

class DataValidator:
    """Validate data quality for ML pipeline"""
    
    @staticmethod
    def validate_sequences(X, y):
        """Validate sequence data"""
        issues = []
        
        # Check shapes
        if len(X) != len(y):
            issues.append(f"Sequence length mismatch: X={len(X)}, y={len(y)}")
        
        # Check for NaN values
        if np.isnan(X).any():
            issues.append(f"NaN values found in X: {np.isnan(X).sum()} values")
        
        if np.isnan(y).any():
            issues.append(f"NaN values found in y: {np.isnan(y).sum()} values")
        
        # Check for infinite values
        if np.isinf(X).any():
            issues.append(f"Infinite values found in X: {np.isinf(X).sum()} values")
        
        if np.isinf(y).any():
            issues.append(f"Infinite values found in y: {np.isinf(y).sum()} values")
        
        # Check data ranges
        if X.min() < -10 or X.max() > 10:
            issues.append(f"X values outside expected range [-10, 10]: min={X.min():.2f}, max={X.max():.2f}")
        
        if y.min() < 0:
            issues.append(f"Negative values in y: min={y.min():.2f}")
        
        return issues
    
    @staticmethod
    def print_data_summary(X, y, dataset_name="Dataset"):
        """Print summary statistics of the data"""
        print(f"\n{dataset_name} Summary:")
        print(f"- X shape: {X.shape}")
        print(f"- y shape: {y.shape}")
        print(f"- X range: [{X.min():.3f}, {X.max():.3f}]")
        print(f"- y range: [{y.min():.3f}, {y.max():.3f}]")
        print(f"- X mean: {X.mean():.3f}, std: {X.std():.3f}")
        print(f"- y mean: {y.mean():.3f}, std: {y.std():.3f}")
        
        # Validate data
        issues = DataValidator.validate_sequences(X, y)
        if issues:
            print(f"- Data issues found: {len(issues)}")
            for issue in issues:
                print(f"  * {issue}")
        else:
            print("- No data quality issues found")

def load_and_validate_data():
    """Load processed data and validate it"""
    print("Loading processed data...")
    
    try:
        data = MLUtils.load_processed_data()
        
        # Validate each dataset
        for dataset_name, (X, y) in [('Training', data['train']), 
                                    ('Validation', data['val']), 
                                    ('Test', data['test'])]:
            DataValidator.print_data_summary(X, y, dataset_name)
        
        print(f"\nMetadata:")
        for key, value in data['metadata'].items():
            print(f"- {key}: {value}")
        
        return data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

if __name__ == '__main__':
    # Test data loading and validation
    data = load_and_validate_data()