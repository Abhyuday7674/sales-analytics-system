from datetime import datetime

# ===== Imports from utils =====
from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)

# =====================================================
# PART 4: REPORT GENERATION
# =====================================================

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report
    """

    with open(output_file, "w", encoding="utf-8") as f:

        # 1. HEADER
        f.write("=" * 50 + "\n")
        f.write("        SALES ANALYTICS REPORT\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"  Records Processed: {len(transactions)}\n")
        f.write("=" * 50 + "\n\n")

        # 2. OVERALL SUMMARY
        total_revenue = calculate_total_revenue(transactions)
        total_transactions = len(transactions)
        avg_order_value = total_revenue / total_transactions if total_transactions else 0

        dates = [tx["Date"] for tx in transactions]
        date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"

        f.write("OVERALL SUMMARY\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions:   {total_transactions}\n")
        f.write(f"Average Order Value:  ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range:           {date_range}\n\n")

        # 3. REGION-WISE PERFORMANCE
        region_stats = region_wise_sales(transactions)

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Region':<10}{'Sales':<15}{'% of Total':<12}{'Transactions'}\n")

        for region, stats in region_stats.items():
            f.write(
                f"{region:<10}₹{stats['total_sales']:,.2f}   "
                f"{stats['percentage']:>6}%        "
                f"{stats['transaction_count']}\n"
            )
        f.write("\n")

        # 4. TOP 5 PRODUCTS
        top_products = top_selling_products(transactions, n=5)

        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Rank':<6}{'Product':<20}{'Qty':<8}{'Revenue'}\n")

        for i, (product, qty, revenue) in enumerate(top_products, start=1):
            f.write(f"{i:<6}{product:<20}{qty:<8}₹{revenue:,.2f}\n")
        f.write("\n")

        # 5. TOP 5 CUSTOMERS
        customers = customer_analysis(transactions)

        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Rank':<6}{'Customer':<12}{'Spent':<15}{'Orders'}\n")

        for i, (cust_id, stats) in enumerate(list(customers.items())[:5], start=1):
            f.write(
                f"{i:<6}{cust_id:<12}₹{stats['total_spent']:,.2f}   "
                f"{stats['purchase_count']}\n"
            )
        f.write("\n")

        # 6. DAILY SALES TREND
        daily_stats = daily_sales_trend(transactions)

        f.write("DAILY SALES TREND\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Date':<12}{'Revenue':<15}{'Txns':<8}{'Customers'}\n")

        for date, stats in daily_stats.items():
            f.write(
                f"{date:<12}₹{stats['revenue']:,.2f}   "
                f"{stats['transaction_count']:<8}"
                f"{stats['unique_customers']}\n"
            )
        f.write("\n")

        # 7. PRODUCT PERFORMANCE ANALYSIS
        peak_day = find_peak_sales_day(transactions)
        low_products = low_performing_products(transactions)

        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 50 + "\n")
        f.write(
            f"Best Sales Day: {peak_day[0]} | "
            f"Revenue: ₹{peak_day[1]:,.2f} | "
            f"Transactions: {peak_day[2]}\n"
        )

        if low_products:
            f.write("Low Performing Products:\n")
            for product, qty, revenue in low_products:
                f.write(f" - {product}: Qty={qty}, Revenue=₹{revenue:,.2f}\n")
        else:
            f.write("No low performing products found.\n")
        f.write("\n")

        # 8. API ENRICHMENT SUMMARY
        enriched_ok = [tx for tx in enriched_transactions if tx["API_Match"]]
        enriched_fail = [tx for tx in enriched_transactions if not tx["API_Match"]]

        success_rate = (
            (len(enriched_ok) / len(enriched_transactions)) * 100
            if enriched_transactions else 0
        )

        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total Records Enriched: {len(enriched_ok)}\n")
        f.write(f"Enrichment Success Rate: {success_rate:.2f}%\n")

        if enriched_fail:
            f.write("Products Not Enriched:\n")
            for tx in enriched_fail:
                f.write(f" - {tx['ProductID']} ({tx['ProductName']})\n")

        f.write("\n")

    print(f"✓ Report saved to: {output_file}")


# =====================================================
# PART 5: MAIN APPLICATION
# =====================================================

def main():
    """
    Main execution function
    """

    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)

        # 1. Read sales data
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        # 2. Parse and clean data
        print("\n[2/10] Parsing and cleaning data...")
        parsed_transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(parsed_transactions)} records")

        # 3. Show filter options
        regions = sorted({tx["Region"] for tx in parsed_transactions if tx["Region"]})

        amounts = [tx["Quantity"] * tx["UnitPrice"] for tx in parsed_transactions]

        print("\n[3/10] Filter Options Available:")
        print("Regions:", ", ".join(regions))
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")

        apply_filter = input("Do you want to filter data? (y/n): ").strip().lower()

        region = None
        min_amount = None
        max_amount = None

        if apply_filter == "y":
            region = input("Enter region (or press Enter to skip): ").strip() or None

            min_val = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_val = input("Enter maximum amount (or press Enter to skip): ").strip()

            min_amount = float(min_val) if min_val else None
            max_amount = float(max_val) if max_val else None

        # 4. Validate & filter
        print("\n[4/10] Validating transactions...")
        valid_transactions, invalid_count, _ = validate_and_filter(
            parsed_transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_transactions)} | Invalid: {invalid_count}")

        # 5. Analysis step (functions reused in report)
        print("\n[5/10] Analyzing sales data...")
        print("✓ Analysis complete")

        # 6. Fetch API products
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products")

        # 7. Enrich sales data
        print("\n[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_count = sum(1 for tx in enriched_transactions if tx["API_Match"])
        success_rate = (
            (enriched_count / len(enriched_transactions)) * 100
            if enriched_transactions else 0
        )
        print(
            f"✓ Enriched {enriched_count}/{len(enriched_transactions)} "
            f"transactions ({success_rate:.1f}%)"
        )

        # 8. Save enriched data
        print("\n[8/10] Saving enriched data...")
        save_enriched_data(enriched_transactions)
        print("✓ Saved to: data/enriched_sales_data.txt")

        # 9. Generate report
        print("\n[9/10] Generating report...")
        generate_sales_report(valid_transactions, enriched_transactions)

        # 10. Finish
        print("\n[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print("\n❌ An unexpected error occurred.")
        print("Details:", str(e))


if __name__ == "__main__":
    main()
