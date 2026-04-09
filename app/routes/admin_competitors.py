from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
from app.utils.auth_decorators import admin_required
from datetime import datetime, date

admin_competitors_bp = Blueprint('admin_competitors', __name__)

@admin_competitors_bp.route('', methods=['POST'])
@admin_required
def create_competitor():
    """Admin: Create new competitor"""
    try:
        data = request.get_json()
        
        required_fields = ['business_name', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        competitor = Competitor(
            business_name=data['business_name'],
            owner_name=data.get('owner_name'),
            category=data['category'],
            location=data.get('location'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        db.session.add(competitor)
        db.session.commit()
        
        return jsonify(competitor.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>', methods=['PUT'])
@admin_required
def update_competitor(competitor_id):
    """Admin: Update competitor"""
    try:
        competitor = Competitor.query.get(competitor_id)
        if not competitor:
            return jsonify({'message': 'Competitor not found'}), 404
        
        data = request.get_json()
        updatable_fields = ['business_name', 'owner_name', 'category', 'location', 'phone', 'email']
        
        for field in updatable_fields:
            if field in data:
                setattr(competitor, field, data[field])
        
        db.session.commit()
        return jsonify(competitor.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>', methods=['DELETE'])
@admin_required
def delete_competitor(competitor_id):
    """Admin: Delete competitor"""
    try:
        competitor = Competitor.query.get(competitor_id)
        if not competitor:
            return jsonify({'message': 'Competitor not found'}), 404
        
        db.session.delete(competitor)
        db.session.commit()
        
        return jsonify({'message': 'Competitor deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>/sales', methods=['POST'])
@admin_required
def add_competitor_sales(competitor_id):
    """Admin: Add sales data for competitor"""
    try:
        competitor = Competitor.query.get(competitor_id)
        if not competitor:
            return jsonify({'message': 'Competitor not found'}), 404
        
        data = request.get_json()
        
        sales = CompetitorSales(
            competitor_id=competitor_id,
            date=datetime.strptime(data.get('date', str(date.today())), '%Y-%m-%d').date(),
            daily_sales=data.get('daily_sales', 0),
            monthly_sales=data.get('monthly_sales', 0),
            yearly_sales=data.get('yearly_sales', 0)
        )
        
        db.session.add(sales)
        db.session.commit()
        
        return jsonify(sales.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>/products', methods=['POST'])
@admin_required
def add_competitor_product(competitor_id):
    """Admin: Add product for competitor"""
    try:
        competitor = Competitor.query.get(competitor_id)
        if not competitor:
            return jsonify({'message': 'Competitor not found'}), 404
        
        data = request.get_json()
        
        required_fields = ['product_name', 'category', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        product = CompetitorProduct(
            competitor_id=competitor_id,
            product_name=data['product_name'],
            category=data['category'],
            price=data['price']
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_competitor_product(competitor_id, product_id):
    """Admin: Update competitor product"""
    try:
        product = CompetitorProduct.query.filter_by(
            id=product_id,
            competitor_id=competitor_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        data = request.get_json()
        updatable_fields = ['product_name', 'category', 'price']
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/<int:competitor_id>/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_competitor_product(competitor_id, product_id):
    """Admin: Delete competitor product"""
    try:
        product = CompetitorProduct.query.filter_by(
            id=product_id,
            competitor_id=competitor_id
        ).first()
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_competitors_bp.route('/all', methods=['GET'])
@admin_required
def get_all_competitors_admin():
    """Admin: Get all competitors (no filtering)"""
    try:
        competitors = Competitor.query.all()
        
        result = []
        for comp in competitors:
            comp_dict = comp.to_dict()
            comp_dict['product_count'] = CompetitorProduct.query.filter_by(competitor_id=comp.id).count()
            comp_dict['sales_records'] = CompetitorSales.query.filter_by(competitor_id=comp.id).count()
            result.append(comp_dict)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
