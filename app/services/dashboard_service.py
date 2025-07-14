import os
import pandas as pd
from flask import current_app
from datetime import datetime

def get_dashboard_data():
    """
    Gathers dynamic data for the main dashboard, including file statuses
    and product counts.
    """
    # Get file paths from the application's configuration
    amazon_file = current_app.config['AMAZON_PROCESSED_FILE']
    asdata_file = current_app.config['ASDATA_PROCESSED_FILE']
    
    dashboard_info = {
        "amazon_status": "Not Found",
        "amazon_last_update": "N/A",
        "amazon_total_products": 0,
        "asdata_status": "Not Found",
        "asdata_last_update": "N/A",
        "asdata_total_products": 0,
        "current_time": datetime.now().strftime("%d %B %Y, %H:%M:%S")
    }

    # --- Check Amazon File ---
    if os.path.exists(amazon_file):
        try:
            # Get last modification time
            m_time = os.path.getmtime(amazon_file)
            dashboard_info["amazon_last_update"] = datetime.fromtimestamp(m_time).strftime('%d-%m-%Y')
            
            # Read file to get product count
            df_amazon = pd.read_csv(amazon_file)
            dashboard_info["amazon_total_products"] = len(df_amazon)
            dashboard_info["amazon_status"] = "Ok"
        except Exception:
            dashboard_info["amazon_status"] = "Error Reading"

    # --- Check ASPoint File ---
    if os.path.exists(asdata_file):
        try:
            # Get last modification time
            m_time = os.path.getmtime(asdata_file)
            dashboard_info["asdata_last_update"] = datetime.fromtimestamp(m_time).strftime('%d-%m-%Y')
            
            # Read file to get product count
            df_asdata = pd.read_csv(asdata_file)
            dashboard_info["asdata_total_products"] = len(df_asdata)
            dashboard_info["asdata_status"] = "Ok"
        except Exception:
            dashboard_info["asdata_status"] = "Error Reading"
            
    return dashboard_info
