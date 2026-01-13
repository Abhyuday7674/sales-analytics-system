# Sales Analytics System

A Python-based Sales Analytics System that processes sales data, performs analytics, enriches product information using an external API, and generates a detailed sales report.

---

```
sales-analytics-system/
├── data/
│   ├── sales_data.txt
│   └── enriched_sales_data.txt
├── output/
│   └── sales_report.txt
├── utils/
│   ├── file_handler.py
│   ├── data_processor.py
│   └── api_handler.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

```bash
## Install required dependencies:
pip install -r requirements.txt


## How to Run the Project
python main.py
```

---

## What the Application Does

```bash
  1.Reads and cleans raw sales data from a text file
  2.Validates transactions and applies optional filters
  3.Performs sales analysis (revenue, trends, top products, customers)
  4.Fetches product data from an external API
  5.Enriches sales transactions with API information
  6.Generates output files and a detailed sales report
```

---

## Output Files

```bash
data/enriched_sales_data.txt
Contains sales data enriched with API product details

output/sales_report.txt
Contains a detailed sales analytics report
```

---

## Requirements

```bash
* Python 3.8 or higher

* requests library
```

---

## Notes
All output files are generated automatically when the program runs

The application handles errors gracefully and does not crash on failures

No hardcoded file paths are used

---






