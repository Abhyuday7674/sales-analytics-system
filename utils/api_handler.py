import requests

BASE_URL = "https://dummyjson.com/products"


def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    Returns: list of product dictionaries
    """
    try:
        response = requests.get(f"{BASE_URL}?limit=100")
        response.raise_for_status()

        data = response.json()
        return data.get("products", [])

    except requests.exceptions.RequestException as e:
        print("Failed to fetch products:", e)
        return []



def get_product_by_id(product_id):
    """
    Fetches a single product by ID
    """

    try:
        response = requests.get(f"{BASE_URL}/{product_id}")
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching product {product_id}:", e)
        return {}


def search_products(query):
    """
    Searches products using a keyword
    """

    try:
        response = requests.get(f"{BASE_URL}/search?q={query}")
        response.raise_for_status()

        data = response.json()
        return data.get("products", [])

    except requests.exceptions.RequestException as e:
        print("Error searching products:", e)
        return []


def create_product_mapping(api_products):
    """
    Creates mapping of API product ID → product info
    """

    product_mapping = {}

    for product in api_products:
        product_id = product.get("id")
        if product_id is None:
            continue

        product_mapping[int(product_id)] = {
            "category": product.get("category"),
            "brand": product.get("brand"),
            "rating": product.get("rating")
        }

    return product_mapping





def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    """

    enriched_transactions = []

    for tx in transactions:
        enriched_tx = tx.copy()

        try:
            # Extract numeric part: P101 → 101
            product_id_str = tx.get("ProductID", "")
            numeric_id = int(product_id_str.replace("P", ""))

            # 🔥 CRITICAL FIX: Map P101 → API ID 1
            api_id = numeric_id - 100

            if api_id in product_mapping:
                api_product = product_mapping[api_id]

                enriched_tx["API_Category"] = api_product["category"]
                enriched_tx["API_Brand"] = api_product["brand"]
                enriched_tx["API_Rating"] = api_product["rating"]
                enriched_tx["API_Match"] = True
            else:
                enriched_tx["API_Category"] = None
                enriched_tx["API_Brand"] = None
                enriched_tx["API_Rating"] = None
                enriched_tx["API_Match"] = False

        except Exception:
            enriched_tx["API_Category"] = None
            enriched_tx["API_Brand"] = None
            enriched_tx["API_Rating"] = None
            enriched_tx["API_Match"] = False

        enriched_transactions.append(enriched_tx)

    return enriched_transactions






def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file
    """

    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    try:
        with open(filename, "w", encoding="utf-8") as file:
            # Write header
            file.write("|".join(headers) + "\n")

            # Write data rows
            for tx in enriched_transactions:
                row = []
                for header in headers:
                    value = tx.get(header)
                    row.append("" if value is None else str(value))

                file.write("|".join(row) + "\n")

        print(f"Enriched data saved successfully to {filename}")

    except Exception as e:
        print("Error saving enriched data:", e)
