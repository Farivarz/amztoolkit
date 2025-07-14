import pandas as pd
import numpy as np
from collections import Counter
from flask import current_app

def clean_ean_series(series):
    """Converts a series containing EANs to clean strings, handling scientific notation."""
    s_cleaned = series.copy().fillna('N/A')
    numeric_mask = pd.to_numeric(s_cleaned, errors='coerce').notna()
    s_cleaned.loc[numeric_mask] = pd.to_numeric(s_cleaned.loc[numeric_mask], errors='coerce').apply(
        lambda x: f'{int(x)}' if pd.notna(x) else 'N/A'
    )
    return s_cleaned

def analyze_fbm_data():
    """
    Analyzes FBM stock levels by reading data from configured file paths,
    grouping SKU variations, and comparing stock levels including Xentral data.
    """
    amazon_file = current_app.config['AMAZON_PROCESSED_FILE']
    asdata_file = current_app.config['ASDATA_PROCESSED_FILE']
    xentral_file = current_app.config['XENTRAL_PROCESSED_FILE']

    # 1. Load Data
    try:
        dtype_spec = {'SellerSKU': str, 'EAN': str, 'ItemNumber': str, 'ean': str}
        df_amazon = pd.read_csv(amazon_file, dtype=dtype_spec)
        df_asdata = pd.read_csv(asdata_file, dtype=dtype_spec)
        df_xentral = pd.read_csv(xentral_file, dtype=dtype_spec)
    except FileNotFoundError as e:
        return {"error": f"File not found: {e.filename}"}

    try:
        # 2. Validate required columns exist
        required_amazon_cols = ['SellerSKU', 'Quantity', 'ItemName', 'EAN']
        required_asdata_cols = ['ItemNumber', 'OnlineStock', 'EAN']
        required_xentral_cols = ['ean', 'stockCount', 'shopPriceDisplay']

        # ... (validation checks for amazon and asdata files) ...

        for col in required_xentral_cols:
            if col not in df_xentral.columns:
                return {"error": f"Missing required column in Xentral file: {col}"}

        # 3. Normalize Data for Processing
        df_amazon['SellerSKU'] = df_amazon['SellerSKU'].str.strip()
        df_asdata['ItemNumber'] = df_asdata['ItemNumber'].str.strip()
        df_amazon['Quantity'] = pd.to_numeric(df_amazon['Quantity'], errors='coerce').fillna(0).astype(int)
        df_asdata['OnlineStock'] = pd.to_numeric(df_asdata['OnlineStock'], errors='coerce').fillna(0).astype(int)
        df_xentral['stockCount'] = pd.to_numeric(df_xentral['stockCount'], errors='coerce').fillna(0).astype(int)
        
        df_amazon['ItemName'] = df_amazon['ItemName'].fillna('N/A')
        
        df_amazon['EAN'] = clean_ean_series(df_amazon['EAN'])
        df_asdata['EAN'] = clean_ean_series(df_asdata['EAN'])
        df_xentral['ean'] = clean_ean_series(df_xentral['ean']) # Clean Xentral EAN

        # 4. Create BaseSKU and filter for FBM-related items
        df_amazon['BaseSKU'] = df_amazon['SellerSKU'].str.replace(r'(fba|fbm|fbs)$', '', regex=True, case=False)
        df_fbm_amazon = df_amazon[~df_amazon['SellerSKU'].str.lower().str.endswith('fba')].copy()
        
        # 5. Group by BaseSKU and aggregate
        df_amazon_grouped = df_fbm_amazon.groupby('BaseSKU').agg(
            FBM_Qty=('Quantity', 'max'),
            ItemName=('ItemName', 'first'),
            EAN=('EAN', 'first'),
            SKU_Variations=('SellerSKU', lambda x: ', '.join(x.unique()))
        ).reset_index()

        # 6. Merge with ASPoint data
        df_merged_as = pd.merge(
            df_amazon_grouped,
            df_asdata[['ItemNumber', 'OnlineStock', 'EAN']],
            left_on='BaseSKU',
            right_on='ItemNumber',
            how='left',
            suffixes=('_amazon', '_asdata')
        )
        df_merged_as['OnlineStock'] = df_merged_as['OnlineStock'].fillna(0).astype(int)

        # 7. Determine final EAN from ASPoint/Amazon
        df_merged_as['Final_EAN'] = np.where(df_merged_as['EAN_asdata'].notna() & (df_merged_as['EAN_asdata'] != 'N/A'), df_merged_as['EAN_asdata'], df_merged_as['EAN_amazon'])

        # 8. Merge with Xentral data based on the Final EAN
        df_final = pd.merge(
            df_merged_as,
            df_xentral[['ean', 'stockCount', 'shopPriceDisplay']],
            left_on='Final_EAN',
            right_on='ean',
            how='left'
        )
        df_final['stockCount'] = df_final['stockCount'].fillna(0).astype(int)
        df_final['shopPriceDisplay'] = df_final['shopPriceDisplay'].fillna('N/A')


        # 9. Determine status
        def get_status(row):
            if row['OnlineStock'] > 0:
                if row['FBM_Qty'] > row['OnlineStock']: return "Wrong"
                if row['FBM_Qty'] == row['OnlineStock']: return "Correct"
                if row['FBM_Qty'] >= (0.5 * row['OnlineStock']): return "Healthy"
                return "Observation"
            else:
                if row['FBM_Qty'] > 0: return "Wrong"
                return "No Stock"

        df_final['FBM_Status'] = df_final.apply(get_status, axis=1)

        # 10. Prepare for JSON output
        df_final = df_final.rename(columns={
            'OnlineStock': 'ASPoint_Stock', 
            'Final_EAN': 'EAN',
            'stockCount': 'Xentral_Stock',
            'shopPriceDisplay': 'Xentral_Price'
        })
        
        processed_results = df_final[['BaseSKU', 'ItemName', 'EAN', 'FBM_Qty', 'ASPoint_Stock', 'FBM_Status', 'SKU_Variations', 'Xentral_Stock', 'Xentral_Price']].to_dict('records')
        fbm_status_counter = Counter(df_final['FBM_Status'])
        
        summary = { "fbm": dict(fbm_status_counter) }
            
        return {"data": processed_results, "count": len(processed_results), "summary": summary}
    
    except Exception as e:
        return {"error": f"An unexpected error occurred during analysis: {e}"}

