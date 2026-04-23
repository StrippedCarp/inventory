from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
from app.models.user import User
from app.models.product import Product
from app.utils.organization_context import get_organization_id, get_user_id
from sqlalchemy import func
from datetime import datetime, timedelta

competitors_bp = Blueprint('competitors', __name__)

@competitors_bp.route('', methods=['GET'])
@jwt_required()
def get_competitors():
    """Get competitors filtered by user's business category and organization"""
    try:
        org_id = get_organization_id()
        user_id = get_user_id()
        
        # Get user's product categories
        user_categories = db.session.query(Product.category).filter_by(
            user_id=user_id,
            organization_id=org_id
        ).distinct().all()
        user_categories = [cat[0] for cat in user_categories]
        
        # Filter competitors by matching categories AND organization
        if user_categories:
            competitors = Competitor.query.filter(
                Competitor.category.in_(user_categories),
                Competitor.organization_id == org_id
            ).all()
        else:
            # If user has no products yet, show no competitors
            competitors = []
        
        result = []
        for comp in competitors:
            comp_dict = comp.to_dict()
            
            # Get latest sales data
            latest_sales = CompetitorSales.query.filter_by(competitor_id=comp.id).order_by(CompetitorSales.date.desc()).first()
            comp_dict['sales_data'] = latest_sales.to_dict() if latest_sales else None
            
            # Get product count
            comp_dict['product_count'] = CompetitorProduct.query.filter_by(competitor_id=comp.id).count()
            
            result.append(comp_dict)
        
        return jsonify({
            'competitors': result,
            'user_categories': user_categories,
            'message': f'Showing competitors in your categories: {", ".join(user_categories)}' if user_categories else 'Add products to see relevant competitors'
        }), 200
    except Exception as e:
        print(f"Competitors error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@competitors_bp.route('/<int:competitor_id>', methods=['GET'])
@jwt_required()
def get_competitor_details(competitor_id):
    """Get detailed competitor information from current organization"""
    try:
        org_id = get_organization_id()
        competitor = Competitor.query.filter_by(id=competitor_id, organization_id=org_id).first()
        if not competitor:
            return jsonify({'message': 'Competitor not found'}), 404
        
        comp_dict = competitor.to_dict()
        
        # Get latest sales data (for sales_data summary)
        latest_sales = CompetitorSales.query.filter_by(competitor_id=competitor_id).order_by(CompetitorSales.date.desc()).first()
        comp_dict['sales_data'] = latest_sales.to_dict() if latest_sales else None
        
        # Get sales history
        sales_history = CompetitorSales.query.filter_by(competitor_id=competitor_id).order_by(CompetitorSales.date.desc()).limit(30).all()
        comp_dict['sales_history'] = [sale.to_dict() for sale in sales_history]
        
        # Get products with pricing
        products = CompetitorProduct.query.filter_by(competitor_id=competitor_id).all()
        comp_dict['products'] = [prod.to_dict() for prod in products]
        
        # Get product count
        comp_dict['product_count'] = len(products)
        
        return jsonify(comp_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competitors_bp.route('/<int:competitor_id>/products', methods=['GET'])
@jwt_required()
def get_competitor_products(competitor_id):
    """Get competitor's products and pricing"""
    try:
        products = CompetitorProduct.query.filter_by(competitor_id=competitor_id).all()
        return jsonify([prod.to_dict() for prod in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competitors_bp.route('/<int:competitor_id>/sales', methods=['GET'])
@jwt_required()
def get_competitor_sales(competitor_id):
    """Get competitor's sales data"""
    try:
        period = request.args.get('period', 'month')  # day, month, year
        
        sales = CompetitorSales.query.filter_by(competitor_id=competitor_id).order_by(CompetitorSales.date.desc())
        
        if period == 'day':
            sales = sales.limit(30)
        elif period == 'month':
            sales = sales.limit(12)
        else:
            sales = sales.limit(5)
        
        return jsonify([sale.to_dict() for sale in sales.all()])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@competitors_bp.route('/comparison', methods=['GET'])
@jwt_required()
def compare_with_competitors():
    """Compare user's business with competitors in same organization"""
    try:
        org_id = get_organization_id()
        user_id = get_user_id()
        
        # Get user's categories
        user_categories = db.session.query(Product.category).filter_by(
            user_id=user_id,
            organization_id=org_id
        ).distinct().all()
        user_categories = [cat[0] for cat in user_categories]
        
        # Get competitors in same categories AND organization
        competitors = Competitor.query.filter(
            Competitor.category.in_(user_categories),
            Competitor.organization_id == org_id
        ).all()
        
        comparison = []
        for comp in competitors:
            latest_sales = CompetitorSales.query.filter_by(competitor_id=comp.id).order_by(CompetitorSales.date.desc()).first()
            
            comparison.append({
                'competitor': comp.to_dict(),
                'sales': latest_sales.to_dict() if latest_sales else None
            })
        
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
