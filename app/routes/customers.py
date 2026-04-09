from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.customer import Customer, CustomerPricing, LoyaltyTransaction
from app.models.sales_transaction import SalesTransaction
from sqlalchemy import func

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def get_customers():
    """Get all customers"""
    try:
        status = request.args.get('status')
        customer_type = request.args.get('type')
        
        query = Customer.query
        
        if status:
            query = query.filter_by(status=status)
        if customer_type:
            query = query.filter_by(customer_type=customer_type)
        
        customers = query.order_by(Customer.name.asc()).all()
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required(optional=True)
def get_customer(customer_id):
    """Get customer details with purchase history"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        customer_dict = customer.to_dict()
        
        # Get purchase history
        sales = SalesTransaction.query.filter_by(customer_id=customer_id).order_by(SalesTransaction.sale_date.desc()).limit(20).all()
        customer_dict['recent_purchases'] = [sale.to_dict() for sale in sales]
        
        # Get loyalty transactions
        loyalty = LoyaltyTransaction.query.filter_by(customer_id=customer_id).order_by(LoyaltyTransaction.created_at.desc()).limit(10).all()
        customer_dict['loyalty_history'] = [l.to_dict() for l in loyalty]
        
        # Get special pricing
        special_prices = CustomerPricing.query.filter_by(customer_id=customer_id).all()
        customer_dict['special_prices'] = [sp.to_dict() for sp in special_prices]
        
        return jsonify(customer_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """Create new customer"""
    try:
        data = request.get_json()
        
        # Check if email already exists
        if data.get('email'):
            existing = Customer.query.filter_by(email=data['email']).first()
            if existing:
                return jsonify({'message': 'Email already exists'}), 400
        
        customer = Customer(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            customer_type=data.get('customer_type', 'regular'),
            discount_percentage=data.get('discount_percentage', 0.0),
            credit_limit=data.get('credit_limit', 0.0),
            notes=data.get('notes')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            customer.name = data['name']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        if 'customer_type' in data:
            customer.customer_type = data['customer_type']
        if 'discount_percentage' in data:
            customer.discount_percentage = data['discount_percentage']
        if 'credit_limit' in data:
            customer.credit_limit = data['credit_limit']
        if 'status' in data:
            customer.status = data['status']
        if 'notes' in data:
            customer.notes = data['notes']
        
        db.session.commit()
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/loyalty', methods=['POST'])
@jwt_required()
def add_loyalty_points(customer_id):
    """Add or redeem loyalty points"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        data = request.get_json()
        points = data['points']
        transaction_type = data['transaction_type']  # earned, redeemed, adjusted
        
        # Update customer points
        customer.loyalty_points += points
        
        # Create transaction record
        transaction = LoyaltyTransaction(
            customer_id=customer_id,
            points=points,
            transaction_type=transaction_type,
            reference_id=data.get('reference_id'),
            description=data.get('description')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'customer_id': customer_id,
            'new_balance': customer.loyalty_points,
            'transaction': transaction.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/special-price', methods=['POST'])
@jwt_required()
def set_special_price(customer_id):
    """Set special price for customer on specific product"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        
        data = request.get_json()
        
        # Check if special price already exists
        existing = CustomerPricing.query.filter_by(
            customer_id=customer_id,
            product_id=data['product_id']
        ).first()
        
        if existing:
            existing.special_price = data['special_price']
        else:
            pricing = CustomerPricing(
                customer_id=customer_id,
                product_id=data['product_id'],
                special_price=data['special_price']
            )
            db.session.add(pricing)
        
        db.session.commit()
        return jsonify({'message': 'Special price set successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/special-price/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_special_price(customer_id, product_id):
    """Remove special price"""
    try:
        pricing = CustomerPricing.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).first()
        
        if not pricing:
            return jsonify({'message': 'Special price not found'}), 404
        
        db.session.delete(pricing)
        db.session.commit()
        
        return jsonify({'message': 'Special price removed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/top', methods=['GET'])
@jwt_required(optional=True)
def get_top_customers():
    """Get top customers by purchase amount"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        customers = Customer.query.filter_by(status='active').order_by(Customer.total_purchases.desc()).limit(limit).all()
        
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/<int:customer_id>/price/<int:product_id>', methods=['GET'])
@jwt_required(optional=True)
def get_customer_price(customer_id, product_id):
    """Get price for customer (special price or regular with discount)"""
    try:
        from app.models.product import Product
        
        customer = Customer.query.get(customer_id)
        product = Product.query.get(product_id)
        
        if not customer or not product:
            return jsonify({'message': 'Customer or product not found'}), 404
        
        # Check for special price
        special = CustomerPricing.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).first()
        
        if special:
            final_price = special.special_price
            price_type = 'special'
        else:
            # Apply customer discount
            final_price = product.price * (1 - customer.discount_percentage / 100)
            price_type = 'discount' if customer.discount_percentage > 0 else 'regular'
        
        return jsonify({
            'product_id': product_id,
            'customer_id': customer_id,
            'regular_price': product.price,
            'final_price': final_price,
            'price_type': price_type,
            'discount_percentage': customer.discount_percentage
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
