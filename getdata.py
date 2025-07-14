import requests
import pandas as pd
import time

def get_all_xentral_products(instance_url, api_token):
    """
    Fetches all products from all pages of the Xentral API and returns them as a single pandas DataFrame.

    Args:
        instance_url (str): The URL of your Xentral instance (e.g., "https://637e1d39a977f.xentral.biz/").
        api_token (str): Your personal access token for the Xentral API.

    Returns:
        pandas.DataFrame: A DataFrame containing all product data, or None if an error occurs.
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
        
    # Convert the final list of all products into a DataFrame
    return pd.DataFrame(all_products_list)


if __name__ == "__main__":
    # --- PLEASE REPLACE THESE VALUES ---
    XENTRAL_INSTANCE_URL = "https://637e1d39a977f.xentral.biz/"
    # IMPORTANT: I cannot save your token. Please paste it here.
    XENTRAL_API_TOKEN = "885|0KhcgVwxa11fvwqAxi1RGqQeWUNTzJseWRkxBsKN"

    # Fetch all product data from all pages
    product_df = get_all_xentral_products(XENTRAL_INSTANCE_URL, XENTRAL_API_TOKEN)

    # If the DataFrame was successfully created, print statistics
    if product_df is not None:
        print("\n--- Final Product Data Statistics ---")

        # Get DataFrame shape
        rows, cols = product_df.shape
        print(f"Total products fetched: {rows}")
        print(f"Total columns per product: {cols}")
        print("-------------------------------------")

