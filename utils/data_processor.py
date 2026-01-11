def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    """

    cleaned_data = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = parts

        # Clean product name
        product_name = product_name.replace(",", "")

        # Clean and convert numeric fields
        quantity = int(quantity.replace(",", ""))
        unit_price = float(unit_price.replace(",", ""))

        transaction = {
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region
        }

        cleaned_data.append(transaction)

    return cleaned_data




def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    """

    valid_transactions = []
    invalid_count = 0

    # Required keys
    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    # Collect regions and amounts for display
    available_regions = set()
    amounts = []

    # ---------------- VALIDATION ----------------
    for tx in transactions:
        # Check required fields
        if not all(field in tx and tx[field] for field in required_fields):
            invalid_count += 1
            continue

        # Validation rules
        if (
            tx["Quantity"] <= 0 or
            tx["UnitPrice"] <= 0 or
            not tx["TransactionID"].startswith("T") or
            not tx["ProductID"].startswith("P") or
            not tx["CustomerID"].startswith("C")
        ):
            invalid_count += 1
            continue

        # Valid transaction
        amount = tx["Quantity"] * tx["UnitPrice"]
        tx["Amount"] = amount

        available_regions.add(tx["Region"])
        amounts.append(amount)

        valid_transactions.append(tx)

    # ---------------- DISPLAY INFO ----------------
    print("Available Regions:", sorted(available_regions))

    if amounts:
        print("Transaction Amount Range:",
              f"Min = {min(amounts)}, Max = {max(amounts)}")

    # ---------------- FILTERING ----------------
    filtered_by_region = 0
    filtered_by_amount = 0

    # Filter by region
    if region:
        before = len(valid_transactions)
        valid_transactions = [
            tx for tx in valid_transactions if tx["Region"] == region
        ]
        filtered_by_region = before - len(valid_transactions)

    # Filter by amount
    if min_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [
            tx for tx in valid_transactions if tx["Amount"] >= min_amount
        ]
        filtered_by_amount += before - len(valid_transactions)

    if max_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [
            tx for tx in valid_transactions if tx["Amount"] <= max_amount
        ]
        filtered_by_amount += before - len(valid_transactions)

    # ---------------- SUMMARY ----------------
    filter_summary = {
        "total_input": len(transactions),
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(valid_transactions)
    }

    return valid_transactions, invalid_count, filter_summary




def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)

    Expected Output: Single number representing sum of (Quantity * UnitPrice)
    Example: 1545000.50
    """

    total_revenue = 0.0

    for tx in transactions:
        total_revenue += tx["Quantity"] * tx["UnitPrice"]

    return total_revenue




def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics
    """

    region_stats = {}
    total_sales_overall = 0.0

    # Step 1: Calculate total sales & transaction count per region
    for tx in transactions:
        region = tx["Region"]
        sale_amount = tx["Quantity"] * tx["UnitPrice"]
        total_sales_overall += sale_amount

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_stats[region]["total_sales"] += sale_amount
        region_stats[region]["transaction_count"] += 1

    # Step 2: Calculate percentage contribution
    for region in region_stats:
        percentage = (
            region_stats[region]["total_sales"] / total_sales_overall
        ) * 100 if total_sales_overall > 0 else 0

        region_stats[region]["percentage"] = round(percentage, 2)

    # Step 3: Sort by total_sales (descending)
    sorted_region_stats = dict(
        sorted(
            region_stats.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_stats




def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    """

    product_stats = {}

    # Step 1: Aggregate quantity and revenue by product
    for tx in transactions:
        product = tx["ProductName"]
        quantity = tx["Quantity"]
        revenue = quantity * tx["UnitPrice"]

        if product not in product_stats:
            product_stats[product] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_stats[product]["total_quantity"] += quantity
        product_stats[product]["total_revenue"] += revenue

    # Step 2: Convert to list of tuples
    product_list = [
        (
            product,
            stats["total_quantity"],
            stats["total_revenue"]
        )
        for product, stats in product_stats.items()
    ]

    # Step 3: Sort by total_quantity (descending)
    product_list.sort(key=lambda x: x[1], reverse=True)

    # Step 4: Return top n products
    return product_list[:n]




def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    """

    customer_stats = {}

    # Step 1: Aggregate customer data
    for tx in transactions:
        customer = tx["CustomerID"]
        product = tx["ProductName"]
        amount = tx["Quantity"] * tx["UnitPrice"]

        if customer not in customer_stats:
            customer_stats[customer] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_stats[customer]["total_spent"] += amount
        customer_stats[customer]["purchase_count"] += 1
        customer_stats[customer]["products_bought"].add(product)

    # Step 2: Calculate averages & finalize structure
    for customer in customer_stats:
        total_spent = customer_stats[customer]["total_spent"]
        purchase_count = customer_stats[customer]["purchase_count"]

        avg_order_value = total_spent / purchase_count if purchase_count > 0 else 0

        customer_stats[customer]["avg_order_value"] = round(avg_order_value, 2)
        customer_stats[customer]["products_bought"] = list(
            customer_stats[customer]["products_bought"]
        )

    # Step 3: Sort by total_spent (descending)
    sorted_customer_stats = dict(
        sorted(
            customer_stats.items(),
            key=lambda item: item[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customer_stats



def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date
    """

    daily_stats = {}

    # Step 1: Group by date
    for tx in transactions:
        date = tx["Date"]
        revenue = tx["Quantity"] * tx["UnitPrice"]
        customer = tx["CustomerID"]

        if date not in daily_stats:
            daily_stats[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily_stats[date]["revenue"] += revenue
        daily_stats[date]["transaction_count"] += 1
        daily_stats[date]["unique_customers"].add(customer)

    # Step 2: Convert customer sets to counts
    for date in daily_stats:
        daily_stats[date]["unique_customers"] = len(
            daily_stats[date]["unique_customers"]
        )

    # Step 3: Sort chronologically by date
    sorted_daily_stats = dict(sorted(daily_stats.items()))

    return sorted_daily_stats



def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)
    """

    daily_totals = {}

    # Step 1: Aggregate revenue and transaction count by date
    for tx in transactions:
        date = tx["Date"]
        revenue = tx["Quantity"] * tx["UnitPrice"]

        if date not in daily_totals:
            daily_totals[date] = {
                "revenue": 0.0,
                "transaction_count": 0
            }

        daily_totals[date]["revenue"] += revenue
        daily_totals[date]["transaction_count"] += 1

    # Step 2: Find the date with maximum revenue
    peak_date = max(
        daily_totals.items(),
        key=lambda item: item[1]["revenue"]
    )

    # Step 3: Extract values
    date = peak_date[0]
    revenue = peak_date[1]["revenue"]
    transaction_count = peak_date[1]["transaction_count"]

    return (date, revenue, transaction_count)



def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales
    """

    product_stats = {}

    # Step 1: Aggregate quantity and revenue per product
    for tx in transactions:
        product = tx["ProductName"]
        quantity = tx["Quantity"]
        revenue = quantity * tx["UnitPrice"]

        if product not in product_stats:
            product_stats[product] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_stats[product]["total_quantity"] += quantity
        product_stats[product]["total_revenue"] += revenue

    # Step 2: Filter low-performing products
    low_performers = [
        (
            product,
            stats["total_quantity"],
            stats["total_revenue"]
        )
        for product, stats in product_stats.items()
        if stats["total_quantity"] < threshold
    ]

    # Step 3: Sort by total_quantity (ascending)
    low_performers.sort(key=lambda x: x[1])

    return low_performers


