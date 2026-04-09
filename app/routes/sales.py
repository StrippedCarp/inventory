from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.sales_transaction import SalesTransaction
from app.models.product import Product
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('', methods=['GET'])
def get_sales():
    """Get sales transactions with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        product_id = request.args.get('product_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = db.session.query(SalesTransaction, Product).join(Product)
        
        # Apply filters
        if product_id:
            query = query.filter(SalesTransaction.product_id == product_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(SalesTransaction.sale_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(SalesTransaction.sale_date <= end)
        
        # Paginate results
        sales = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = {
            'sales': [
                {
                    **sale.to_dict(),
                    'product_name': product.name,
                    'product_sku': product.sku
                }
                for sale, product in sales.items
            ],
            'total': sales.total,
            'pages': sales.pages,
            'current_page': page
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/analytics/daily', methods=['GET'])
def get_daily_sales():
    """Get daily sales analytics for the last 30 days"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        daily_sales = db.session.query(
            SalesTransaction.sale_date,
            func.sum(SalesTransaction.quantity_sold).label('total_quantity'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(SalesTransaction.id).label('transaction_count')
        ).filter(
            SalesTransaction.sale_date >= start_date,
            SalesTransaction.sale_date <= end_date
        ).group_by(SalesTransaction.sale_date).order_by(SalesTransaction.sale_date).all()
        
        result = [
            {
                'date': sale.sale_date.isoformat(),
                'total_quantity': sale.total_quantity or 0,
                'total_revenue': float(sale.total_revenue or 0),
                'transaction_count': sale.transaction_count or 0
            }
            for sale in daily_sales
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/analytics/top-products', methods=['GET'])
def get_top_selling_products():
    """Get top selling products by quantity and revenue"""
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        start_date = date.today() - timedelta(days=days)
        
        top_products = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(SalesTransaction.quantity_sold).label('total_quantity'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(SalesTransaction.id).label('transaction_count')
        ).join(SalesTransaction).filter(
            SalesTransaction.sale_date >= start_date
        ).group_by(
            Product.id, Product.name, Product.sku
        ).order_by(
            func.sum(SalesTransaction.quantity_sold).desc()
        ).limit(limit).all()
        
        result = [
            {
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'total_quantity_sold': product.total_quantity or 0,
                'total_revenue': float(product.total_revenue or 0),
                'transaction_count': product.transaction_count or 0
            }
            for product in top_products
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/analytics/monthly', methods=['GET'])
def get_monthly_sales():
    """Get monthly sales analytics for the last 12 months"""
    try:
        monthly_sales = db.session.query(
            extract('year', SalesTransaction.sale_date).label('year'),
            extract('month', SalesTransaction.sale_date).label('month'),
            func.sum(SalesTransaction.quantity_sold).label('total_quantity'),
            func.sum(SalesTransaction.total_amount).label('total_revenue')
        ).filter(
            SalesTransaction.sale_date >= date.today() - timedelta(days=365)
        ).group_by(
            extract('year', SalesTransaction.sale_date),
            extract('month', SalesTransaction.sale_date)
        ).order_by('year', 'month').all()
        
        result = [
            {
                'year': int(sale.year),
                'month': int(sale.month),
                'total_quantity': sale.total_quantity or 0,
                'total_revenue': float(sale.total_revenue or 0)
            }
            for sale in monthly_sales
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500