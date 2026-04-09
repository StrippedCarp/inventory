#!/usr/bin/env python3
"""
Simplified Data Preprocessing for ML Pipeline
Creates sample data for training when database is not available
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

class SimpleDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.lookback_days = 30
        self.forecast_days = 7
        
    def create_sample_data(self):
        """Create realistic sample sales data"""
        print("Creating sample sales data...")
        
        # Create 5 products with different patterns
        products = [
            {'id': 1, 'name': 'Widget A', 'category': 'Electronics', 'base_demand': 15},
            {'id': 2, 'name': 'Widget B', 'category': 'Hardware', 'base_demand': 8},
            {'id': 3, 'name': 'Widget C', 'category': 'Office', 'base_demand': 12},
            {'id': 4, 'name': 'Widget D', 'category': 'Electronics', 'base_demand': 20},
            {'id': 5, 'name': 'Widget E', 'category': 'Food', 'base_demand': 25}
        ]
        
        # Generate 12 months of data
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        all_data = []
        
        for product in products:
            for current_date in date_range:
                # Add seasonality and trends
                day_of_year = current_date.timetuple().tm_yday
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
                
                # Weekly pattern (lower on weekends)
                weekly_factor = 0.7 if current_date.weekday() >= 5 else 1.0
                
                # Random variation
                random_factor = np.random.normal(1.0, 0.3)
                
                # Calculate daily sales
                daily_sales = max(0, int(
                    product['base_demand'] * seasonal_factor * weekly_factor * random_factor
                ))
                
                all_data.append({
                    'product_id': product['id'],
                    'sale_date': current_date,
                    'quantity_sold': daily_sales,
                    'name': product['name'],
                    'category': product['category']
                })
        
        df = pd.DataFrame(all_data)
        print(f"Created {len(df)} sales records for {len(products)} products")
        return df
    
    def create_time_features(self, df):
        """Create time-based features"""
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
        
        return df
    
    def create_lag_features(self, df):
        """Create lag and rolling features"""
        df = df.copy()
        df = df.sort_values(['product_id', 'sale_date'])
        
        # Create features for each product
        for product_id in df['product_id'].unique():
            mask = df['product_id'] == product_id
            product_data = df.loc[mask, 'quantity_sold']
            
            # Lag features
            for lag in [1, 3, 7, 14, 30]:
                df.loc[mask, f'lag_{lag}'] = product_data.shift(lag)
            
            # Rolling statistics
            for window in [3, 7, 14, 30]:
                df.loc[mask, f'rolling_mean_{window}'] = product_data.rolling(window).mean()
                df.loc[mask, f'rolling_std_{window}'] = product_data.rolling(window).std()
        
        # Fill NaN values
        df = df.ffill().fillna(0)
        return df
    
    def prepare_sequences(self, df):
        """Prepare sequences for ML training"""
        sequences = []
        targets = []
        
        feature_cols = [col for col in df.columns if col not in [
            'product_id', 'sale_date', 'name', 'category', 'quantity_sold'
        ]]
        
        for product_id in df['product_id'].unique():
            product_data = df[df['product_id'] == product_id].sort_values('sale_date')
            
            if len(product_data) < self.lookback_days + self.forecast_days:
                continue
            
            features = product_data[feature_cols].values
            target = product_data['quantity_sold'].values
            
            # Create sequences
            for i in range(len(product_data) - self.lookback_days - self.forecast_days + 1):
                seq_x = features[i:i + self.lookback_days]
                seq_y = target[i + self.lookback_days:i + self.lookback_days + self.forecast_days]
                
                sequences.append(seq_x)
                targets.append(seq_y)
        
        sequences = np.array(sequences)
        targets = np.array(targets)
        
        print(f"Created {len(sequences)} sequences")
        print(f"Sequence shape: {sequences.shape}")
        print(f"Target shape: {targets.shape}")
        
        return sequences, targets, feature_cols
    
    def split_and_normalize_data(self, sequences, targets):
        """Split and normalize data"""
        n_samples = len(sequences)
        
        # Split indices
        test_idx = int(n_samples * 0.85)
        val_idx = int(test_idx * 0.85)
        
        # Split data
        X_train = sequences[:val_idx]
        y_train = targets[:val_idx]
        
        X_val = sequences[val_idx:test_idx]
        y_val = targets[val_idx:test_idx]
        
        X_test = sequences[test_idx:]
        y_test = targets[test_idx:]
        
        # Normalize features
        n_samples_train, n_timesteps, n_features = X_train.shape
        X_train_reshaped = X_train.reshape(-1, n_features)
        
        # Fit scaler
        self.scaler.fit(X_train_reshaped)
        
        # Transform all datasets
        X_train_scaled = self.scaler.transform(X_train_reshaped).reshape(n_samples_train, n_timesteps, n_features)
        
        X_val_reshaped = X_val.reshape(-1, n_features)
        X_val_scaled = self.scaler.transform(X_val_reshaped).reshape(X_val.shape)
        
        X_test_reshaped = X_test.reshape(-1, n_features)
        X_test_scaled = self.scaler.transform(X_test_reshaped).reshape(X_test.shape)
        
        print(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return (X_train_scaled, y_train), (X_val_scaled, y_val), (X_test_scaled, y_test)
    
    def save_processed_data(self, train_data, val_data, test_data, feature_cols):
        """Save processed data"""
        os.makedirs('ml/data', exist_ok=True)
        
        # Save datasets
        np.savez('ml/data/train_data.npz', X=train_data[0], y=train_data[1])
        np.savez('ml/data/val_data.npz', X=val_data[0], y=val_data[1])
        np.savez('ml/data/test_data.npz', X=test_data[0], y=test_data[1])
        
        # Save scaler and metadata
        with open('ml/data/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        metadata = {
            'feature_columns': feature_cols,
            'lookback_days': self.lookback_days,
            'forecast_days': self.forecast_days,
            'n_features': len(feature_cols)
        }
        
        with open('ml/data/metadata.pkl', 'wb') as f:
            pickle.dump(metadata, f)
        
        print("Processed data saved to ml/data/")
    
    def run_preprocessing(self):
        """Run complete preprocessing pipeline"""
        print("Starting simplified data preprocessing...")
        
        # Create sample data
        df = self.create_sample_data()
        
        # Create features
        df_with_time = self.create_time_features(df)
        df_with_lags = self.create_lag_features(df_with_time)
        
        # Prepare sequences
        sequences, targets, feature_cols = self.prepare_sequences(df_with_lags)
        
        # Split and normalize
        train_data, val_data, test_data = self.split_and_normalize_data(sequences, targets)
        
        # Save data
        self.save_processed_data(train_data, val_data, test_data, feature_cols)
        
        print("Data preprocessing completed successfully!")
        return train_data, val_data, test_data, feature_cols

def main():
    preprocessor = SimpleDataPreprocessor()
    train_data, val_data, test_data, feature_cols = preprocessor.run_preprocessing()
    
    print(f"\nFinal dataset shapes:")
    print(f"Training: X={train_data[0].shape}, y={train_data[1].shape}")
    print(f"Validation: X={val_data[0].shape}, y={val_data[1].shape}")
    print(f"Test: X={test_data[0].shape}, y={test_data[1].shape}")
    print(f"Features: {len(feature_cols)}")

if __name__ == '__main__':
    main()