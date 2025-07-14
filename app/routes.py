from flask import render_template, redirect, url_for, jsonify, send_file, current_app as app, request
from app.services.analysis_service import analyze_fbm_data
from app.services.dashboard_service import get_dashboard_data
import pandas as pd
import io
from datetime import datetime

@app.route('/')
def index():
    """Redirects the base URL to the main dashboard."""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """
    Renders the main dashboard page, gathering data from the dashboard service.
    """
    dashboard_data = get_dashboard_data()
    return render_template('dashboard.html', title='Dashboard', data=dashboard_data)

@app.route('/analyzer')
def analyzer_page():
    """
    Renders the FBM Stock Analyzer page.
    """
    return render_template('analyzer.html', title='FBM Stock Analyzer')

@app.route('/fba_order_form', methods=['GET'])
def fba_order_form_page():
    """
    Renders the FBA Order Form page, passing dynamic data.
    """
    user_name = "Default User" 
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    form_data = {
        "user_name": user_name,
        "creation_date": creation_date
    }
    return render_template('fba_order_form.html', title='FBA Order Form', data=form_data)

@app.route('/fba_order/submit', methods=['POST'])
def submit_fba_order():
    """
    Placeholder route to handle the submission of the final FBA order table.
    """
    shipment_data = request.form.to_dict(flat=False)
    print("Received FBA Shipment Data:", shipment_data) 
    return redirect(url_for('fba_order_form_page'))


@app.route('/api/get_product_details')
def get_product_details():
    """
    API endpoint to get product details based on ASIN.
    """
    asin_query = request.args.get('asin', '')
    if not asin_query:
        return jsonify({"error": "ASIN parameter is missing"}), 400

    try:
        amazon_file = app.config['AMAZON_PROCESSED_FILE']
        df = pd.read_csv(amazon_file, dtype=str)
        
        product_data = df[df['ASIN'].str.lower() == asin_query.lower()].iloc[0]
        
        response_data = {
            "sku": product_data.get('SellerSKU', 'Not Found'),
            "product_name": product_data.get('ItemName', 'Not Found'),
            "ean": product_data.get('EAN', 'Not Found')
        }
        return jsonify(response_data)

    except (FileNotFoundError, IndexError):
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/process_data')
def process_data():
    """
    API endpoint that runs the FBM analysis and returns data as JSON.
    """
    analysis_result = analyze_fbm_data()
    return jsonify(analysis_result)

@app.route('/download_fbm_report')
def download_fbm_report():
    """
    Generates an Excel file from the analysis data and sends it for download.
    """
    analysis_result = analyze_fbm_data()
    
    if "error" in analysis_result:
        return f"Could not generate file due to an error: {analysis_result['error']}", 500

    df_export = pd.DataFrame(analysis_result.get("data", []))
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Stock_Analysis')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='fbm_stock_analysis_report.xlsx'
    )
