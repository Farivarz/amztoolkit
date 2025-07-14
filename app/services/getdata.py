import requests
import pandas as pd
import time
import os
import json

def get_all_xentral_products(instance_url, api_token):
    """
    Fetches all products from all pages of the Xentral API and returns them as a list of dictionaries.

    Args:
        instance_url (str): The URL of your Xentral instance (e.g., "https://637e1d39a977f.xentral.biz/").
        api_token (str): Your personal access token for the Xentral API.

    Returns:
        list: A list of dictionaries, where each dictionary is a product. Returns None on error.
    """
    # The '/products' endpoint is the standard way to list all product resources.
    api_endpoint = f"{instance_url}api/v1/products"
    all_products_list = []
    current_page = 1
    page_size = 100 # Define how many products to fetch per page

    # Set up the authorization headers
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    print("Starting to fetch product data from all pages...")

    # Loop indefinitely until the API returns no more products
    while True:
        # Set up the pagination parameters in the format required by the Xentral API
        params = {
            'page[number]': current_page,
            'page[size]': page_size
        }
        
        print(f"Fetching page {current_page}...")

        try:
            # Make the GET request to the Xentral API with the correct parameters
            response = requests.get(api_endpoint, headers=headers, params=params)
            response.raise_for_status() # Raise an exception for bad status codes

            # Convert the JSON response to a dictionary
            products_data = response.json()

            # The actual product list is within the 'data' key
            products_on_page = products_data.get('data')

            if products_on_page:
                all_products_list.extend(products_on_page)
                print(f"Found {len(products_on_page)} products on this page.")
                # If the number of products returned is less than the page size,
                # it must be the last page, so we can stop.
                if len(products_on_page) < page_size:
                    print("This was the last page of products. Stopping.")
                    break
            else:
                # Stop if a page returns no data
                print(f"No more product data found on page {current_page}. Stopping.")
                break
            
            # Move to the next page
            current_page += 1

            # Be a good API citizen and wait a moment before the next request
            time.sleep(0.5) 

        except requests.exceptions.RequestException as e:
            print(f"An error occurred with the API request: {e}")
            if 'response' in locals() and response is not None:
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    if not all_products_list:
        print("No products were fetched.")
        return None
        
    # Return the complete list of product dictionaries
    return all_products_list


if __name__ == "__main__":
    # --- PLEASE REPLACE THESE VALUES ---
    XENTRAL_INSTANCE_URL = "https://637e1d39a977f.xentral.biz/"
    # IMPORTANT: I cannot save your token. Please paste it here.
    XENTRAL_API_TOKEN = "885|0KhcgVwxa11fvwqAxi1RGqQeWUNTzJseWRkxBsKN"

    # Fetch all product data from all pages
    product_list = get_all_xentral_products(XENTRAL_INSTANCE_URL, XENTRAL_API_TOKEN)

    # If the product list was successfully created, clean the data and save it
    if product_list:
        print("\nData fetching complete. Now cleaning and flattening data...")
        
        # Use pandas json_normalize to flatten the nested dictionaries.
        product_df = pd.json_normalize(product_list, sep='_')

        # Define the list of columns to be removed
        columns_to_drop = [
            'standardSupplier', 'manufacturerNumber', 'options', 'selectedOptions',
            'variants', 'variantOf', 'thumbnailId', 'tags', 'freeFields',
            'regionOfOrigin', 'internalComment', 'minimumOrderQuantity',
            'minimumStorageQuantity', 'salesTax', 'hasBatches', 'serialNumbersMode',
            'hasBestBeforeDate', 'hasBillOfMaterials', 'isAssembledJustInTime',
            'isProductionProduct', 'isExternallyProduced', 'allowPurchaseFromAllSuppliers',
            'disabledReason', 'hidePriceOnDocuments', 'ageRating', 'isStockTakingDisabled',
            'hideJustInTimeItemsOnDocuments', 'isShippingCostsProduct',
            'stockStats_purchasedCount', 'category_id', 'stockStats_totalCount',
            'stockStats_availableCount', 'stockStats_inProductionCount',
            'purchasePriceNet_currency', 'purchasePriceGross_currency',
            'purchasePriceGross_amount', 'salesPriceNet_currency', 'salesPriceNet_amount',
            'salesPriceGross_currency', 'salesPriceGross_amount', 'measurements_weight_unit',
            'measurements_netWeight_value', 'measurements_length_unit',
            'measurements_netWeight_unit', 'measurements_width_unit',
            'measurements_height_unit', 'discount_isDiscountProduct',
            'discount_discountPercentage', 'stockTaking_hasStockTakingValue',
            'calculatedPurchasePrice_hasCalculatedPurchasePrice',
            'calculatedPurchasePrice_price_amount', 'calculatedPurchasePrice_price_currency',
            'unit_name',
            # Additional columns to drop from the new request
            'textsAndDescriptions_inCatalog', 'textsAndDescriptions_primaryLanguage_name',
            'textsAndDescriptions_primaryLanguage_shortDescription', 'textsAndDescriptions_primaryLanguage_description',
            'textsAndDescriptions_primaryLanguage_metaTitle', 'textsAndDescriptions_primaryLanguage_metaDescription',
            'textsAndDescriptions_primaryLanguage_metaKeywords', 'textsAndDescriptions_primaryLanguage_catalogName',
            'textsAndDescriptions_primaryLanguage_catalogText', 'textsAndDescriptions_english_name',
            'textsAndDescriptions_english_shortDescription', 'textsAndDescriptions_english_description',
            'textsAndDescriptions_english_shopDescription', 'textsAndDescriptions_english_metaTitle',
            'textsAndDescriptions_english_metaDescription', 'textsAndDescriptions_english_metaKeywords',
            'textsAndDescriptions_english_catalogName', 'textsAndDescriptions_english_catalogText',
            'category', 'standardSupplier_id', 'variantOf_id'
        ]
        
        # Drop the specified columns from the DataFrame
        # The 'errors='ignore'' argument prevents an error if a column doesn't exist
        product_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
        print(f"Removed {len(columns_to_drop)} specified columns.")

        # Some columns might still contain complex objects (lists of dictionaries).
        # We will convert these to a JSON string so they fit in a single CSV cell.
        for col in product_df.columns:
            # Check if the first non-null value in the column is a list or dict
            if not product_df[col].dropna().empty:
                first_value = product_df[col].dropna().iloc[0]
                if isinstance(first_value, (list, dict)):
                    print(f"Converting complex column '{col}' to JSON string.")
                    # Apply json.dumps to each cell in the column
                    product_df[col] = product_df[col].apply(lambda x: json.dumps(x) if x else None)

        print("\n--- Final Product Data Statistics ---")
        # Get DataFrame shape
        rows, cols = product_df.shape
        print(f"Total products fetched: {rows}")
        print(f"Total columns after cleaning: {cols}")
        print("-------------------------------------")

        # Define the output directory and file path
        output_dir = os.path.join('data', 'source')
        output_file = os.path.join(output_dir, 'products_cleaned.csv')

        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the cleaned DataFrame to a CSV file
        product_df.to_csv(output_file, index=False)
        
        print(f"\nCleaned data successfully saved to: {output_file}")
