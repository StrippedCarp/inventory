from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app import db
from app.utils.organization_context import get_organization_id
from app.models.sales_transaction import SalesTransaction
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.supplier import Supplier
from app.models import Forecast, Alert
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, case
import pandas as pd
import io
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        org_id = get_organization_id()
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        # Sales trends (last 90 days)
        daily_sales = db.session.query(
            SalesTransaction.sale_date,
            func.sum(SalesTransaction.quantity_sold).label('total_quantity'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(SalesTransaction.id).label('transaction_count')
        ).join(Product).filter(
            Product.organization_id == org_id,
            SalesTransaction.sale_date >= start_date
        ).group_by(SalesTransaction.sale_date).order_by(SalesTransaction.sale_date).all()
        
        # Inventory turnover by category
        category_turnover = db.session.query(
            Product.category,
            func.sum(SalesTransaction.quantity_sold).label('total_sold'),
            func.avg(Inventory.quantity_on_hand).label('avg_inventory'),
            func.sum(SalesTransaction.total_amount).label('total_revenue')
        ).join(SalesTransaction, Product.id == SalesTransaction.product_id
        ).join(Inventory, Product.id == Inventory.product_id
        ).filter(
            Product.organization_id == org_id,
            SalesTransaction.sale_date >= start_date
        ).group_by(Product.category).all()
        
        # Top selling products
        top_products = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(SalesTransaction.quantity_sold).label('total_sold'),
            func.sum(SalesTransaction.total_amount).label('total_revenue')
        ).join(SalesTransaction, Product.id == SalesTransaction.product_id
        ).filter(
            Product.organization_id == org_id,
            SalesTransaction.sale_date >= start_date
        ).group_by(Product.id, Product.name, Product.sku).order_by(
            func.sum(SalesTransaction.quantity_sold).desc()
        ).limit(10).all()
        
        # Stock status distribution
        stock_status = db.session.query(
            func.count().label('count'),
            case(
                (Inventory.quantity_on_hand == 0, 'out_of_stock'),
                (Inventory.quantity_on_hand <= Product.reorder_point, 'low_stock'),
                else_='in_stock'
            ).label('status')
        ).join(Product, Inventory.product_id == Product.id).filter(
            Product.organization_id == org_id
        ).group_by('status').all()
        
        # Forecast accuracy (if available)
        forecast_accuracy = db.session.query(
            func.avg(Forecast.confidence_score).label('avg_confidence'),
            func.count(Forecast.id).label('total_forecasts')
        ).filter(
            Forecast.forecast_date >= start_date
        ).first()
        
        # KPIs
        total_products = Product.query.filter_by(organization_id=org_id).count()
        total_inventory_value = db.session.query(
            func.sum(Inventory.quantity_on_hand * Product.unit_price)
        ).join(Product, Inventory.product_id == Product.id).filter(
            Product.organization_id == org_id
        ).scalar() or 0
        
        avg_turnover = 0  # Simplified to avoid complex calculation
        
        stockout_count = db.session.query(func.count()).select_from(Inventory).join(Product).filter(
            Product.organization_id == org_id,
            Inventory.quantity_on_hand == 0
        ).scalar() or 0
        stockout_rate = (stockout_count / max(total_products, 1)) * 100
        
        return jsonify({
            'sales_trends': [
                {
                    'date': sale.sale_date.isoformat(),
                    'quantity': sale.total_quantity or 0,
                    'revenue': float(sale.total_revenue or 0),
                    'transactions': sale.transaction_count or 0
                }
                for sale in daily_sales
            ],
            'category_performance': [
                {
                    'category': cat.category,
                    'total_sold': cat.total_sold or 0,
                    'avg_inventory': float(cat.avg_inventory or 0),
                    'revenue': float(cat.total_revenue or 0),
                    'turnover_ratio': (cat.total_sold or 0) / max(cat.avg_inventory or 1, 1)
                }
                for cat in category_turnover
            ],
            'top_products': [
                {
                    'product_id': prod.id,
                    'name': prod.name,
                    'sku': prod.sku,
                    'total_sold': prod.total_sold or 0,
                    'revenue': float(prod.total_revenue or 0)
                }
                for prod in top_products
            ],
            'stock_distribution': [
                {
                    'status': status.status,
                    'count': status.count
                }
                for status in stock_status
            ],
            'kpis': {
                'total_products': total_products,
                'total_inventory_value': float(total_inventory_value),
                'avg_inventory_turnover': float(avg_turnover),
                'stockout_rate': float(stockout_rate),
                'forecast_accuracy': float(forecast_accuracy.avg_confidence or 0) if forecast_accuracy else 0,
                'total_forecasts': forecast_accuracy.total_forecasts if forecast_accuracy else 0
            }
        })
        
    except Exception as e:
        print(f"Analytics dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/inventory-valuation', methods=['GET'])
def get_inventory_valuation():
    """Get detailed inventory valuation report"""
    try:
        valuation_data = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.category,
            Product.unit_price,
            Inventory.quantity_on_hand,
            Supplier.name.label('supplier_name'),
            (Inventory.quantity_on_hand * Product.unit_price).label('total_value')
        ).join(Inventory).join(Supplier).all()
        
        # Group by category
        category_totals = {}
        total_value = 0
        
        items = []
        for item in valuation_data:
            item_data = {
                'product_id': item.id,
                'name': item.name,
                'sku': item.sku,
                'category': item.category,
                'unit_price': float(item.unit_price),
                'quantity': item.quantity_on_hand,
                'supplier': item.supplier_name,
                'total_value': float(item.total_value or 0)
            }
            items.append(item_data)
            
            # Category totals
            if item.category not in category_totals:
                category_totals[item.category] = {'quantity': 0, 'value': 0, 'items': 0}
            
            category_totals[item.category]['quantity'] += item.quantity_on_hand
            category_totals[item.category]['value'] += float(item.total_value or 0)
            category_totals[item.category]['items'] += 1
            
            total_value += float(item.total_value or 0)
        
        return jsonify({
            'items': items,
            'category_summary': [
                {
                    'category': cat,
                    'total_quantity': data['quantity'],
                    'total_value': data['value'],
                    'item_count': data['items'],
                    'percentage_of_total': (data['value'] / max(total_value, 1)) * 100
                }
                for cat, data in category_totals.items()
            ],
            'grand_total': total_value,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/sales-performance', methods=['GET'])
def get_sales_performance():
    """Get sales performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Monthly sales performance
        monthly_sales = db.session.query(
            extract('year', SalesTransaction.sale_date).label('year'),
            extract('month', SalesTransaction.sale_date).label('month'),
            func.sum(SalesTransaction.quantity_sold).label('total_quantity'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(func.distinct(SalesTransaction.product_id)).label('unique_products')
        ).filter(
            SalesTransaction.sale_date >= start_date
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        # Product performance
        product_performance = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            func.sum(SalesTransaction.quantity_sold).label('total_sold'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(SalesTransaction.id).label('transaction_count'),
            func.avg(SalesTransaction.quantity_sold).label('avg_quantity_per_sale')
        ).join(SalesTransaction).filter(
            SalesTransaction.sale_date >= start_date
        ).group_by(Product.id, Product.name, Product.category).all()
        
        # Calculate growth rates
        current_month_sales = db.session.query(
            func.sum(SalesTransaction.total_amount)
        ).filter(
            SalesTransaction.sale_date >= date.today().replace(day=1)
        ).scalar() or 0
        
        previous_month_start = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        previous_month_end = date.today().replace(day=1) - timedelta(days=1)
        
        previous_month_sales = db.session.query(
            func.sum(SalesTransaction.total_amount)
        ).filter(
            SalesTransaction.sale_date >= previous_month_start,
            SalesTransaction.sale_date <= previous_month_end
        ).scalar() or 0
        
        growth_rate = ((current_month_sales - previous_month_sales) / max(previous_month_sales, 1)) * 100
        
        return jsonify({
            'monthly_trends': [
                {
                    'year': int(month.year),
                    'month': int(month.month),
                    'total_quantity': month.total_quantity or 0,
                    'total_revenue': float(month.total_revenue or 0),
                    'unique_products': month.unique_products or 0
                }
                for month in monthly_sales
            ],
            'product_performance': [
                {
                    'product_id': prod.id,
                    'name': prod.name,
                    'category': prod.category,
                    'total_sold': prod.total_sold or 0,
                    'total_revenue': float(prod.total_revenue or 0),
                    'transaction_count': prod.transaction_count or 0,
                    'avg_quantity_per_sale': float(prod.avg_quantity_per_sale or 0)
                }
                for prod in product_performance
            ],
            'performance_metrics': {
                'current_month_sales': float(current_month_sales),
                'previous_month_sales': float(previous_month_sales),
                'growth_rate': float(growth_rate),
                'period_days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/forecast-accuracy', methods=['GET'])
def get_forecast_accuracy():
    """Get forecast accuracy analysis"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Forecast accuracy by product
        forecast_accuracy = db.session.query(
            Product.id,
            Product.name,
            func.avg(Forecast.confidence_score).label('avg_confidence'),
            func.count(Forecast.id).label('forecast_count'),
            func.avg(Forecast.predicted_demand).label('avg_predicted')
        ).join(Forecast).filter(
            Forecast.forecast_date >= start_date
        ).group_by(Product.id, Product.name).all()
        
        # Overall accuracy trends
        accuracy_trends = db.session.query(
            Forecast.forecast_date,
            func.avg(Forecast.confidence_score).label('daily_confidence'),
            func.count(Forecast.id).label('forecast_count')
        ).filter(
            Forecast.forecast_date >= start_date
        ).group_by(Forecast.forecast_date).order_by(Forecast.forecast_date).all()
        
        return jsonify({
            'product_accuracy': [
                {
                    'product_id': acc.id,
                    'product_name': acc.name,
                    'avg_confidence': float(acc.avg_confidence or 0),
                    'forecast_count': acc.forecast_count or 0,
                    'avg_predicted_demand': float(acc.avg_predicted or 0)
                }
                for acc in forecast_accuracy
            ],
            'accuracy_trends': [
                {
                    'date': trend.forecast_date.isoformat(),
                    'confidence': float(trend.daily_confidence or 0),
                    'forecast_count': trend.forecast_count or 0
                }
                for trend in accuracy_trends
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/inventory-report', methods=['GET'])
def export_inventory_report():
    """Export inventory report as Excel, CSV, or PDF"""
    output = None
    try:
        report_format = request.args.get('format', 'xlsx')
        
        # Get inventory data
        inventory_data = db.session.query(
            Product.sku,
            Product.name,
            Product.category,
            Product.unit_price,
            Inventory.quantity_on_hand,
            Product.reorder_point,
            Supplier.name.label('supplier_name'),
            (Inventory.quantity_on_hand * Product.unit_price).label('total_value')
        ).join(Inventory, Product.id == Inventory.product_id
        ).join(Supplier, Product.supplier_id == Supplier.id).all()
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                'SKU': item.sku,
                'Product Name': item.name,
                'Category': item.category,
                'Unit Price': float(item.unit_price),
                'Current Stock': item.quantity_on_hand,
                'Reorder Point': item.reorder_point,
                'Supplier': item.supplier_name,
                'Total Value': float(item.total_value or 0),
                'Status': 'Low Stock' if item.quantity_on_hand <= item.reorder_point else 'OK'
            }
            for item in inventory_data
        ])
        
        if report_format == 'pdf':
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            elements.append(Paragraph(f"<b>Inventory Report - {date.today().isoformat()}</b>", styles['Title']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_text = f"Total Products: {len(df)} | Total Value: KES {df['Total Value'].sum():,.2f} | Low Stock: {len(df[df['Status'] == 'Low Stock'])}"
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Table data (limit to first 50 rows for PDF)
            table_data = [['SKU', 'Product', 'Category', 'Stock', 'Value']]
            for _, row in df.head(50).iterrows():
                table_data.append([
                    str(row['SKU'])[:15],
                    str(row['Product Name'])[:25],
                    str(row['Category'])[:15],
                    str(row['Current Stock']),
                    f"{row['Total Value']:.0f}"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            if len(df) > 50:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(f"<i>Showing first 50 of {len(df)} items. Download Excel for full report.</i>", styles['Normal']))
            
            doc.build(elements)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'inventory_report_{date.today().isoformat()}.pdf'
            )
        
        elif report_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'inventory_report_{date.today().isoformat()}.csv'
            )
        
        else:  # xlsx
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Inventory Report', index=False)
                
                # Add summary sheet
                summary_df = pd.DataFrame([
                    {'Metric': 'Total Products', 'Value': len(df)},
                    {'Metric': 'Total Inventory Value', 'Value': df['Total Value'].sum()},
                    {'Metric': 'Low Stock Items', 'Value': len(df[df['Status'] == 'Low Stock'])},
                    {'Metric': 'Report Generated', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                ])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'inventory_report_{date.today().isoformat()}.xlsx'
            )
        
    except Exception as e:
        if output:
            try:
                output.close()
            except:
                pass
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/sales-report', methods=['GET'])
def export_sales_report():
    """Export sales report as CSV, Excel, or PDF"""
    output = None
    try:
        report_format = request.args.get('format', 'xlsx')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category', 'all')
        
        if not start_date or not end_date:
            days = request.args.get('days', 30, type=int)
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
        else:
            start_date = datetime.fromisoformat(start_date).date()
            end_date = datetime.fromisoformat(end_date).date()
        
        # Get sales data
        query = db.session.query(
            SalesTransaction.sale_date,
            Product.sku,
            Product.name,
            Product.category,
            SalesTransaction.quantity_sold,
            SalesTransaction.unit_price,
            SalesTransaction.total_amount
        ).join(Product).filter(
            SalesTransaction.sale_date >= start_date,
            SalesTransaction.sale_date <= end_date
        )
        
        if category != 'all':
            query = query.filter(Product.category == category)
        
        sales_data = query.order_by(SalesTransaction.sale_date.desc()).all()
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                'Date': item.sale_date.isoformat(),
                'SKU': item.sku,
                'Product Name': item.name,
                'Category': item.category,
                'Quantity Sold': item.quantity_sold,
                'Unit Price': float(item.unit_price),
                'Total Amount': float(item.total_amount)
            }
            for item in sales_data
        ])
        
        if report_format == 'pdf':
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph(f"<b>Sales Report</b>", styles['Title']))
            elements.append(Paragraph(f"{start_date.isoformat()} to {end_date.isoformat()}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            summary_text = f"Total Sales: KES {df['Total Amount'].sum():,.2f} | Transactions: {len(df)} | Units Sold: {df['Quantity Sold'].sum()}"
            elements.append(Paragraph(summary_text, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            table_data = [['Date', 'Product', 'Qty', 'Amount']]
            for _, row in df.head(50).iterrows():
                table_data.append([
                    str(row['Date']),
                    str(row['Product Name'])[:30],
                    str(row['Quantity Sold']),
                    f"{row['Total Amount']:.0f}"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            
            if len(df) > 50:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(f"<i>Showing first 50 of {len(df)} transactions.</i>", styles['Normal']))
            
            doc.build(elements)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'sales_report_{start_date.isoformat()}_to_{end_date.isoformat()}.pdf'
            )
        
        elif report_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'sales_report_{start_date.isoformat()}_to_{end_date.isoformat()}.csv'
            )
        
        else:  # xlsx
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sales Report', index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'sales_report_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx'
            )
        
    except Exception as e:
        if output:
            try:
                output.close()
            except:
                pass
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/export/low-stock-report', methods=['GET'])
def export_low_stock_report():
    """Export low stock report"""
    try:
        # Get low stock items
        low_stock_data = db.session.query(
            Product.sku,
            Product.name,
            Product.category,
            Product.unit_price,
            Inventory.quantity_on_hand,
            Product.reorder_point,
            Product.safety_stock,
            Supplier.name.label('supplier_name'),
            Supplier.email.label('supplier_email'),
            Supplier.phone.label('supplier_phone')
        ).join(Inventory).join(Supplier).filter(
            Inventory.quantity_on_hand <= Product.reorder_point
        ).all()
        
        df = pd.DataFrame([
            {
                'SKU': item.sku,
                'Product Name': item.name,
                'Category': item.category,
                'Current Stock': item.quantity_on_hand,
                'Reorder Point': item.reorder_point,
                'Safety Stock': item.safety_stock,
                'Shortage': item.reorder_point - item.quantity_on_hand,
                'Unit Price': float(item.unit_price),
                'Supplier': item.supplier_name,
                'Supplier Email': item.supplier_email,
                'Supplier Phone': item.supplier_phone
            }
            for item in low_stock_data
        ])
        
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Low Stock Items', index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'low_stock_report_{date.today().isoformat()}.xlsx'
            )
        finally:
            output.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/product-performance', methods=['GET'])
def export_product_performance():
    """Export product performance report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
        else:
            start_date = datetime.fromisoformat(start_date).date()
            end_date = datetime.fromisoformat(end_date).date()
        
        performance_data = db.session.query(
            Product.sku,
            Product.name,
            Product.category,
            Product.unit_price,
            func.sum(SalesTransaction.quantity_sold).label('total_sold'),
            func.sum(SalesTransaction.total_amount).label('total_revenue'),
            func.count(SalesTransaction.id).label('transaction_count'),
            func.avg(SalesTransaction.quantity_sold).label('avg_quantity_per_sale')
        ).join(SalesTransaction).filter(
            SalesTransaction.sale_date >= start_date,
            SalesTransaction.sale_date <= end_date
        ).group_by(Product.id, Product.sku, Product.name, Product.category, Product.unit_price).all()
        
        df = pd.DataFrame([
            {
                'SKU': item.sku,
                'Product Name': item.name,
                'Category': item.category,
                'Unit Price': float(item.unit_price),
                'Total Units Sold': item.total_sold or 0,
                'Total Revenue': float(item.total_revenue or 0),
                'Number of Transactions': item.transaction_count or 0,
                'Avg Quantity per Sale': float(item.avg_quantity_per_sale or 0)
            }
            for item in performance_data
        ])
        
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Product Performance', index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'product_performance_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx'
            )
        finally:
            output.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/supplier-report', methods=['GET'])
def export_supplier_report():
    """Export supplier report"""
    try:
        suppliers_data = db.session.query(
            Supplier.name,
            Supplier.email,
            Supplier.phone,
            Supplier.address,
            func.count(Product.id).label('product_count')
        ).outerjoin(Product).group_by(
            Supplier.id, Supplier.name, Supplier.email, Supplier.phone, Supplier.address
        ).all()
        
        df = pd.DataFrame([
            {
                'Supplier Name': item.name,
                'Email': item.email,
                'Phone': item.phone,
                'Address': item.address,
                'Products Supplied': item.product_count or 0
            }
            for item in suppliers_data
        ])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Suppliers', index=False)
        
        output.seek(0)
        file_data = output.read()
        output.close()
        
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'supplier_report_{date.today().isoformat()}.xlsx'
        )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/customer-report', methods=['GET'])
def export_customer_report():
    """Export customer report"""
    try:
        from app.models.customer import Customer
        
        customers_data = Customer.query.all()
        
        df = pd.DataFrame([
            {
                'Customer Name': customer.name,
                'Email': customer.email,
                'Phone': customer.phone,
                'Customer Type': customer.customer_type,
                'Loyalty Points': customer.loyalty_points,
                'Total Purchases': float(customer.total_purchases),
                'Discount %': customer.discount_percentage,
                'Credit Limit': float(customer.credit_limit),
                'Outstanding Balance': float(customer.outstanding_balance),
                'Status': customer.status
            }
            for customer in customers_data
        ])
        
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Customers', index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'customer_report_{date.today().isoformat()}.xlsx'
            )
        finally:
            output.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/batch-expiry-report', methods=['GET'])
def export_batch_expiry_report():
    """Export batch expiry report"""
    try:
        from app.models.batch import Batch
        
        batches_data = db.session.query(
            Batch.batch_number,
            Product.name.label('product_name'),
            Product.category,
            Batch.quantity,
            Batch.cost_per_unit,
            Batch.manufacture_date,
            Batch.expiry_date,
            Supplier.name.label('supplier_name'),
            Batch.status
        ).join(Product).outerjoin(Supplier).filter(
            Batch.status == 'active'
        ).order_by(Batch.expiry_date).all()
        
        df = pd.DataFrame([
            {
                'Batch Number': item.batch_number,
                'Product': item.product_name,
                'Category': item.category,
                'Quantity': item.quantity,
                'Cost per Unit': float(item.cost_per_unit),
                'Total Value': float(item.quantity * item.cost_per_unit),
                'Manufacture Date': item.manufacture_date.isoformat() if item.manufacture_date else '',
                'Expiry Date': item.expiry_date.isoformat() if item.expiry_date else '',
                'Days Until Expiry': (item.expiry_date - date.today()).days if item.expiry_date else '',
                'Supplier': item.supplier_name or '',
                'Status': item.status
            }
            for item in batches_data
        ])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Batch Expiry', index=False)
        
        output.seek(0)
        file_data = output.read()
        output.close()
        
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'batch_expiry_report_{date.today().isoformat()}.xlsx'
        )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/profit-loss-report', methods=['GET'])
def export_profit_loss_report():
    """Export profit and loss report"""
    try:
        from app.models.batch import Batch
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date).date()
            end_date = datetime.fromisoformat(end_date).date()
        
        sales_data = db.session.query(
            SalesTransaction.sale_date,
            Product.category,
            func.sum(SalesTransaction.total_amount).label('revenue'),
            func.sum(SalesTransaction.quantity_sold).label('units_sold')
        ).join(Product).filter(
            SalesTransaction.sale_date >= start_date,
            SalesTransaction.sale_date <= end_date
        ).group_by(SalesTransaction.sale_date, Product.category).all()
        
        avg_costs = db.session.query(
            Product.category,
            func.avg(Batch.cost_per_unit).label('avg_cost')
        ).join(Product).group_by(Product.category).all()
        
        cost_dict = {item.category: float(item.avg_cost or 0) for item in avg_costs}
        
        df = pd.DataFrame([
            {
                'Date': item.sale_date.isoformat(),
                'Category': item.category,
                'Revenue': float(item.revenue or 0),
                'Units Sold': item.units_sold or 0,
                'Avg Cost per Unit': cost_dict.get(item.category, 0),
                'COGS': (item.units_sold or 0) * cost_dict.get(item.category, 0),
                'Gross Profit': float(item.revenue or 0) - ((item.units_sold or 0) * cost_dict.get(item.category, 0)),
                'Gross Margin %': ((float(item.revenue or 0) - ((item.units_sold or 0) * cost_dict.get(item.category, 0))) / float(item.revenue or 1)) * 100 if item.revenue else 0
            }
            for item in sales_data
        ])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Profit & Loss', index=False)
            
            summary_df = pd.DataFrame([
                {'Metric': 'Total Revenue', 'Value': df['Revenue'].sum()},
                {'Metric': 'Total COGS', 'Value': df['COGS'].sum()},
                {'Metric': 'Gross Profit', 'Value': df['Gross Profit'].sum()},
                {'Metric': 'Gross Margin %', 'Value': (df['Gross Profit'].sum() / df['Revenue'].sum() * 100) if df['Revenue'].sum() > 0 else 0}
            ])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        file_data = output.read()
        output.close()
        
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'profit_loss_report_{start_date.isoformat()}_to_{end_date.isoformat()}.xlsx'
        )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
