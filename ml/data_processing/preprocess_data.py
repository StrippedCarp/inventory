#!/usr/bin/env python3
"""
Data preprocessing pipeline for demand forecasting
Fetches sales data from PostgreSQL and creates time-series features for LSTM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

from app import create_app, db
from app.models.sales_transaction import SalesTransaction
from app.models.product import Product

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.lookback_days = 30
        self.forecast_days = 7
        
    def fetch_sales_data(self):
        """Fetch sales transaction data from database"""
        app = create_app()
        
        with app.app_context():
            # Get sales data with product information
            query = db.session.query(
                SalesTransaction.product_id,
                SalesTransaction.sale_date,
                SalesTransaction.quantity_sold,
                SalesTransaction.unit_price,
                SalesTransaction.total_amount,
                Product.name,
                Product.category
            ).join(Product).order_by(
                SalesTransaction.product_id,
                SalesTransaction.sale_date
            )
            
            # Convert to DataFrame
            df = pd.read_sql(query.statement, db.engine)
            
        print(f"Fetched {len(df)} sales records")
        return df
    
    def create_daily_aggregates(self, df):
        """Create daily sales aggregates by product"""
        # Group by product and date, sum quantities
        daily_sales = df.groupby(['product_id', 'sale_date']).agg({
            'quantity_sold': 'sum',
            'total_amount': 'sum',
            'name': 'first',
            'category': 'first'
        }).reset_index()
        
        # Create complete date range for each product
        products = daily_sales['product_id'].unique()
        date_range = pd.date_range(
            start=daily_sales['sale_date'].min(),
            end=daily_sales['sale_date'].max(),
            freq='D'
        )
        
        complete_data = []
        for product_id in products:
            product_data = daily_sales[daily_sales['product_id'] == product_id]
            product_info = product_data.iloc[0]
            
            # Create complete date series
            product_dates = pd.DataFrame({
                'product_id': product_id,
                'sale_date': date_range,
                'name': product_info['name'],
                'category': product_info['category']
            })
            
            # Merge with actual sales data
            merged = product_dates.merge(
                product_data[['sale_date', 'quantity_sold', 'total_amount']], 
                on='sale_date', 
                how='left'
            )
            
            # Fill missing values with 0
            merged['quantity_sold'] = merged['quantity_sold'].fillna(0)
            merged['total_amount'] = merged['total_amount'].fillna(0)
            
            complete_data.append(merged)
        
        result = pd.concat(complete_data, ignore_index=True)
        print(f"Created daily aggregates: {len(result)} records")
        return result
    
    def create_time_features(self, df):
        """Create time-based features"""
        df = df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Basic time features
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['day_of_month'] = df['sale_date'].dt.day
        df['month'] = df['sale_date'].dt.month
        df['quarter'] = df['sale_date'].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df['sale_date'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['sale_date'].dt.is_month_end.astype(int)
        
        # Cyclical encoding for periodic features
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        print("Created time-based features")
        return df
    
    def create_lag_features(self, df):
        """Create lag and rolling window features"""
        df = df.copy()
        df = df.sort_values(['product_id', 'sale_date'])
        
        # Create lag features for each product
        lag_periods = [1, 3, 7, 14, 30]
        rolling_windows = [3, 7, 14, 30]
        
        for product_id in df['product_id'].unique():
            mask = df['product_id'] == product_id
            product_data = df.loc[mask, 'quantity_sold']
            
            # Lag features
            for lag in lag_periods:
                df.loc[mask, f'lag_{lag}'] = product_data.shift(lag)
            
            # Rolling statistics
            for window in rolling_windows:
                df.loc[mask, f'rolling_mean_{window}'] = product_data.rolling(window).mean()
                df.loc[mask, f'rolling_std_{window}'] = product_data.rolling(window).std()
                df.loc[mask, f'rolling_min_{window}'] = product_data.rolling(window).min()
                df.loc[mask, f'rolling_max_{window}'] = product_data.rolling(window).max()
        
        # Fill NaN values with forward fill then backward fill
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        print("Created lag and rolling features")
        return df
    
    def create_trend_features(self, df):
        """Create trend and seasonality features"""
        df = df.copy()
        df = df.sort_values(['product_id', 'sale_date'])
        
        for product_id in df['product_id'].unique():
            mask = df['product_id'] == product_id
            product_data = df.loc[mask, 'quantity_sold']
            
            # Simple trend (difference from previous day)
            df.loc[mask, 'trend_1d'] = product_data.diff()
            
            # Weekly trend (difference from same day last week)
            df.loc[mask, 'trend_7d'] = product_data.diff(7)
            
            # Growth rate
            df.loc[mask, 'growth_rate'] = product_data.pct_change()
            
        # Fill NaN values
        df = df.fillna(0)
        
        print("Created trend features")
        return df
    
    def prepare_sequences(self, df, target_col='quantity_sold'):
        """Prepare sequences for LSTM training"""
        sequences = []
        targets = []
        product_ids = []
        
        feature_cols = [col for col in df.columns if col not in [
            'product_id', 'sale_date', 'name', 'category', target_col
        ]]
        
        for product_id in df['product_id'].unique():
            product_data = df[df['product_id'] == product_id].sort_values('sale_date')
            
            if len(product_data) < self.lookback_days + self.forecast_days:
                continue
            
            # Normalize features for this product
            features = product_data[feature_cols].values
            target = product_data[target_col].values
            
            # Create sequences
            for i in range(len(product_data) - self.lookback_days - self.forecast_days + 1):
                # Input sequence
                seq_x = features[i:i + self.lookback_days]
                # Target (next forecast_days)
                seq_y = target[i + self.lookback_days:i + self.lookback_days + self.forecast_days]
                
                sequences.append(seq_x)
                targets.append(seq_y)
                product_ids.append(product_id)
        
        sequences = np.array(sequences)
        targets = np.array(targets)
        
        print(f"Created {len(sequences)} sequences for LSTM training")
        print(f"Sequence shape: {sequences.shape}")
        print(f"Target shape: {targets.shape}")
        
        return sequences, targets, np.array(product_ids), feature_cols
    
    def split_data(self, sequences, targets, product_ids, test_size=0.15, val_size=0.15):
        """Split data into train/validation/test sets"""
        n_samples = len(sequences)
        
        # Calculate split indices
        test_idx = int(n_samples * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size))
        
        # Split data
        X_train = sequences[:val_idx]
        y_train = targets[:val_idx]
        
        X_val = sequences[val_idx:test_idx]
        y_val = targets[val_idx:test_idx]
        
        X_test = sequences[test_idx:]
        y_test = targets[test_idx:]
        
        print(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
    
    def normalize_data(self, train_data, val_data, test_data):
        """Normalize features using StandardScaler"""
        X_train, y_train = train_data
        X_val, y_val = val_data
        X_test, y_test = test_data
        
        # Reshape for scaling
        n_samples, n_timesteps, n_features = X_train.shape
        X_train_reshaped = X_train.reshape(-1, n_features)
        
        # Fit scaler on training data
        self.scaler.fit(X_train_reshaped)
        
        # Transform all datasets
        X_train_scaled = self.scaler.transform(X_train_reshaped).reshape(n_samples, n_timesteps, n_features)
        
        X_val_reshaped = X_val.reshape(-1, n_features)
        X_val_scaled = self.scaler.transform(X_val_reshaped).reshape(X_val.shape)
        
        X_test_reshaped = X_test.reshape(-1, n_features)
        X_test_scaled = self.scaler.transform(X_test_reshaped).reshape(X_test.shape)
        
        print("Data normalized using StandardScaler")
        
        return (X_train_scaled, y_train), (X_val_scaled, y_val), (X_test_scaled, y_test)
    
    def save_processed_data(self, train_data, val_data, test_data, feature_cols):
        """Save processed data and scaler"""
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
        """Run the complete preprocessing pipeline"""
        print("Starting data preprocessing pipeline...")
        
        # Step 1: Fetch data
        df = self.fetch_sales_data()
        
        # Step 2: Create daily aggregates
        daily_df = self.create_daily_aggregates(df)
        
        # Step 3: Create time features
        df_with_time = self.create_time_features(daily_df)
        
        # Step 4: Create lag features
        df_with_lags = self.create_lag_features(df_with_time)
        
        # Step 5: Create trend features
        df_final = self.create_trend_features(df_with_lags)
        
        # Step 6: Prepare sequences
        sequences, targets, product_ids, feature_cols = self.prepare_sequences(df_final)
        
        # Step 7: Split data
        train_data, val_data, test_data = self.split_data(sequences, targets, product_ids)
        
        # Step 8: Normalize data
        train_norm, val_norm, test_norm = self.normalize_data(train_data, val_data, test_data)
        
        # Step 9: Save processed data
        self.save_processed_data(train_norm, val_norm, test_norm, feature_cols)
        
        print("Data preprocessing completed successfully!")
        
        return train_norm, val_norm, test_norm, feature_cols

def main():
    preprocessor = DataPreprocessor()
    train_data, val_data, test_data, feature_cols = preprocessor.run_preprocessing()
    
    print(f"\nFinal dataset shapes:")
    print(f"Training: X={train_data[0].shape}, y={train_data[1].shape}")
    print(f"Validation: X={val_data[0].shape}, y={val_data[1].shape}")
    print(f"Test: X={test_data[0].shape}, y={test_data[1].shape}")
    print(f"Features: {len(feature_cols)}")

if __name__ == '__main__':
    main()