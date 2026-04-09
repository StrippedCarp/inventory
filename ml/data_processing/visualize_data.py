#!/usr/bin/env python3
"""
Data visualization and exploratory analysis for demand forecasting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from app import create_app, db
from app.models.sales_transaction import SalesTransaction
from app.models.product import Product

class DataVisualizer:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.figsize = (12, 8)
        
    def fetch_and_prepare_data(self):
        """Fetch and prepare data for visualization"""
        app = create_app()
        
        with app.app_context():
            query = db.session.query(
                SalesTransaction.product_id,
                SalesTransaction.sale_date,
                SalesTransaction.quantity_sold,
                SalesTransaction.total_amount,
                Product.name,
                Product.category
            ).join(Product).order_by(SalesTransaction.sale_date)
            
            df = pd.read_sql(query.statement, db.engine)
            
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        return df
    
    def plot_sales_trends(self, df):
        """Plot overall sales trends"""
        # Daily sales trend
        daily_sales = df.groupby('sale_date').agg({
            'quantity_sold': 'sum',
            'total_amount': 'sum'
        }).reset_index()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize)
        
        # Quantity trend
        ax1.plot(daily_sales['sale_date'], daily_sales['quantity_sold'], linewidth=2)
        ax1.set_title('Daily Sales Quantity Trend', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Quantity Sold')
        ax1.grid(True, alpha=0.3)
        
        # Revenue trend
        ax2.plot(daily_sales['sale_date'], daily_sales['total_amount'], linewidth=2, color='green')
        ax2.set_title('Daily Sales Revenue Trend', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Revenue ($)')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ml/data/sales_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_seasonality_analysis(self, df):
        """Analyze and plot seasonality patterns"""
        df['day_of_week'] = df['sale_date'].dt.day_name()
        df['month'] = df['sale_date'].dt.month_name()
        df['hour'] = df['sale_date'].dt.hour
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Day of week pattern
        dow_sales = df.groupby('day_of_week')['quantity_sold'].sum()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_sales = dow_sales.reindex(dow_order)
        
        axes[0, 0].bar(dow_sales.index, dow_sales.values, color='skyblue')
        axes[0, 0].set_title('Sales by Day of Week', fontweight='bold')
        axes[0, 0].set_ylabel('Total Quantity Sold')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Monthly pattern
        monthly_sales = df.groupby('month')['quantity_sold'].sum()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_sales = monthly_sales.reindex(month_order)
        
        axes[0, 1].bar(monthly_sales.index, monthly_sales.values, color='lightcoral')
        axes[0, 1].set_title('Sales by Month', fontweight='bold')
        axes[0, 1].set_ylabel('Total Quantity Sold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Category distribution
        category_sales = df.groupby('category')['quantity_sold'].sum().sort_values(ascending=False)
        axes[1, 0].pie(category_sales.values, labels=category_sales.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Sales Distribution by Category', fontweight='bold')
        
        # Top products
        top_products = df.groupby('name')['quantity_sold'].sum().sort_values(ascending=False).head(10)
        axes[1, 1].barh(range(len(top_products)), top_products.values, color='lightgreen')
        axes[1, 1].set_yticks(range(len(top_products)))
        axes[1, 1].set_yticklabels(top_products.index)
        axes[1, 1].set_title('Top 10 Products by Sales Volume', fontweight='bold')
        axes[1, 1].set_xlabel('Total Quantity Sold')
        
        plt.tight_layout()
        plt.savefig('ml/data/seasonality_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_correlation_matrix(self, df):
        """Plot correlation matrix of numerical features"""
        # Create time-based features for correlation analysis
        df_corr = df.copy()
        df_corr['day_of_week'] = df_corr['sale_date'].dt.dayofweek
        df_corr['month'] = df_corr['sale_date'].dt.month
        df_corr['day_of_month'] = df_corr['sale_date'].dt.day
        df_corr['is_weekend'] = (df_corr['day_of_week'] >= 5).astype(int)
        
        # Select numerical columns
        numerical_cols = ['quantity_sold', 'total_amount', 'day_of_week', 'month', 
                         'day_of_month', 'is_weekend']
        
        correlation_matrix = df_corr[numerical_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('ml/data/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_product_specific_trends(self, df, top_n=5):
        """Plot trends for top N products"""
        # Get top products by total sales
        top_products = df.groupby(['product_id', 'name'])['quantity_sold'].sum().sort_values(ascending=False).head(top_n)
        
        fig, axes = plt.subplots(top_n, 1, figsize=(15, 3*top_n))
        if top_n == 1:
            axes = [axes]
            
        for i, (product_info, total_sales) in enumerate(top_products.items()):
            product_id, product_name = product_info
            product_data = df[df['product_id'] == product_id]
            
            # Daily sales for this product
            daily_product_sales = product_data.groupby('sale_date')['quantity_sold'].sum()
            
            axes[i].plot(daily_product_sales.index, daily_product_sales.values, linewidth=2)
            axes[i].set_title(f'{product_name} - Daily Sales Trend', fontweight='bold')
            axes[i].set_ylabel('Quantity Sold')
            axes[i].grid(True, alpha=0.3)
            
            # Add 7-day moving average
            ma_7 = daily_product_sales.rolling(window=7).mean()
            axes[i].plot(ma_7.index, ma_7.values, '--', alpha=0.7, label='7-day MA')
            axes[i].legend()
        
        plt.tight_layout()
        plt.savefig('ml/data/product_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_demand_distribution(self, df):
        """Plot demand distribution analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Overall demand distribution
        axes[0, 0].hist(df['quantity_sold'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribution of Daily Demand', fontweight='bold')
        axes[0, 0].set_xlabel('Quantity Sold')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(df['quantity_sold'].mean(), color='red', linestyle='--', label=f'Mean: {df["quantity_sold"].mean():.1f}')
        axes[0, 0].legend()
        
        # Log-scale distribution
        non_zero_sales = df[df['quantity_sold'] > 0]['quantity_sold']
        axes[0, 1].hist(np.log1p(non_zero_sales), bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
        axes[0, 1].set_title('Log Distribution of Non-Zero Demand', fontweight='bold')
        axes[0, 1].set_xlabel('Log(Quantity Sold + 1)')
        axes[0, 1].set_ylabel('Frequency')
        
        # Demand by category
        category_demand = df.groupby('category')['quantity_sold'].agg(['mean', 'std']).reset_index()
        x_pos = np.arange(len(category_demand))
        
        axes[1, 0].bar(x_pos, category_demand['mean'], yerr=category_demand['std'], 
                      capsize=5, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[1, 0].set_title('Average Demand by Category', fontweight='bold')
        axes[1, 0].set_xlabel('Category')
        axes[1, 0].set_ylabel('Average Quantity Sold')
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(category_demand['category'], rotation=45)
        
        # Demand variability (coefficient of variation)
        product_stats = df.groupby(['product_id', 'name'])['quantity_sold'].agg(['mean', 'std']).reset_index()
        product_stats['cv'] = product_stats['std'] / product_stats['mean']
        product_stats = product_stats.dropna().sort_values('cv', ascending=False).head(10)
        
        axes[1, 1].barh(range(len(product_stats)), product_stats['cv'], color='orange', alpha=0.7)
        axes[1, 1].set_yticks(range(len(product_stats)))
        axes[1, 1].set_yticklabels(product_stats['name'], fontsize=8)
        axes[1, 1].set_title('Top 10 Most Variable Products (CV)', fontweight='bold')
        axes[1, 1].set_xlabel('Coefficient of Variation')
        
        plt.tight_layout()
        plt.savefig('ml/data/demand_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def generate_summary_report(self, df):
        """Generate summary statistics report"""
        print("="*60)
        print("DEMAND FORECASTING DATA ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nDataset Overview:")
        print(f"- Total records: {len(df):,}")
        print(f"- Date range: {df['sale_date'].min()} to {df['sale_date'].max()}")
        print(f"- Number of products: {df['product_id'].nunique()}")
        print(f"- Number of categories: {df['category'].nunique()}")
        
        print(f"\nSales Statistics:")
        print(f"- Total quantity sold: {df['quantity_sold'].sum():,}")
        print(f"- Total revenue: ${df['total_amount'].sum():,.2f}")
        print(f"- Average daily demand: {df['quantity_sold'].mean():.2f}")
        print(f"- Demand standard deviation: {df['quantity_sold'].std():.2f}")
        
        print(f"\nTop 5 Products by Volume:")
        top_products = df.groupby('name')['quantity_sold'].sum().sort_values(ascending=False).head(5)
        for i, (product, quantity) in enumerate(top_products.items(), 1):
            print(f"{i}. {product}: {quantity:,} units")
        
        print(f"\nTop 5 Categories by Volume:")
        top_categories = df.groupby('category')['quantity_sold'].sum().sort_values(ascending=False).head(5)
        for i, (category, quantity) in enumerate(top_categories.items(), 1):
            print(f"{i}. {category}: {quantity:,} units")
        
        print(f"\nData Quality:")
        print(f"- Zero sales days: {(df['quantity_sold'] == 0).sum():,} ({(df['quantity_sold'] == 0).mean()*100:.1f}%)")
        print(f"- Missing values: {df.isnull().sum().sum()}")
        
        # Save report to file
        os.makedirs('ml/data', exist_ok=True)
        with open('ml/data/analysis_report.txt', 'w') as f:
            f.write("DEMAND FORECASTING DATA ANALYSIS REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Dataset Overview:\n")
            f.write(f"- Total records: {len(df):,}\n")
            f.write(f"- Date range: {df['sale_date'].min()} to {df['sale_date'].max()}\n")
            f.write(f"- Number of products: {df['product_id'].nunique()}\n")
            f.write(f"- Number of categories: {df['category'].nunique()}\n\n")
            # Add more details as needed
        
        print(f"\nReport saved to: ml/data/analysis_report.txt")
        
    def run_analysis(self):
        """Run complete data analysis and visualization"""
        print("Starting data analysis and visualization...")
        
        # Create output directory
        os.makedirs('ml/data', exist_ok=True)
        
        # Fetch data
        df = self.fetch_and_prepare_data()
        
        # Generate visualizations
        print("Generating sales trend plots...")
        self.plot_sales_trends(df)
        
        print("Generating seasonality analysis...")
        self.plot_seasonality_analysis(df)
        
        print("Generating correlation matrix...")
        self.plot_correlation_matrix(df)
        
        print("Generating product-specific trends...")
        self.plot_product_specific_trends(df)
        
        print("Generating demand distribution analysis...")
        self.plot_demand_distribution(df)
        
        # Generate summary report
        print("Generating summary report...")
        self.generate_summary_report(df)
        
        print("Analysis completed! Check ml/data/ for generated plots and reports.")

def main():
    visualizer = DataVisualizer()
    visualizer.run_analysis()

if __name__ == '__main__':
    main()