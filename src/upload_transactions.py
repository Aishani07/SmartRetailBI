
import os
import requests
import pandas as pd
from dotenv import load_dotenv

print("========== SMARTRETAIL DATA UPLOAD ==========")

load_dotenv()

cloudant_url = os.getenv("CLOUDANT_URL").rstrip("/")
username = os.getenv("CLOUDANT_USERNAME")
password = os.getenv("CLOUDANT_PASSWORD")

database_name = "smartretail"
database_url = f"{cloudant_url}/{database_name}"

# Read cleaned dataset
df = pd.read_csv(
    "data/processed/cleaned_retail.csv",
    low_memory=False,
    dtype={"InvoiceNo": str, "StockCode": str}
)

print("Transaction rows loaded:", len(df))

# Check current database
try:
    check = requests.get(
        database_url,
        auth=(username, password),
        timeout=30
    )
    check.raise_for_status()

    existing_count = check.json().get("doc_count", 0)

    if existing_count > 0:
        print("Database already contains documents.")
        print("Current document count:", existing_count)
        print("Upload stopped to avoid duplicate records.")
        raise SystemExit

    batch = []
    uploaded = 0
    batch_size = 500

    # Group transaction rows by invoice
    for invoice_no, group in df.groupby("InvoiceNo", sort=False):

        first_row = group.iloc[0]

        customer_id = first_row["CustomerID"]

        if pd.isna(customer_id):
            customer_id = None
        else:
            customer_id = int(customer_id)

        items = []

        for _, row in group.iterrows():
            items.append({
                "stock_code": str(row["StockCode"]),
                "description": str(row["Description"]),
                "quantity": int(row["Quantity"]),
                "unit_price": float(row["UnitPrice"]),
                "revenue": float(row["Revenue"])
            })

        invoice_document = {
            "_id": "invoice_" + str(invoice_no),
            "document_type": "invoice",
            "invoice_number": str(invoice_no),
            "invoice_date": pd.to_datetime(
                first_row["InvoiceDate"]
            ).isoformat(),
            "customer_id": customer_id,
            "country": str(first_row["Country"]),
            "total_revenue": round(group["Revenue"].sum(), 2),
            "items": items
        }

        batch.append(invoice_document)

        # Upload every 500 invoices
        if len(batch) >= batch_size:

            response = requests.post(
                f"{database_url}/_bulk_docs",
                auth=(username, password),
                json={"docs": batch},
                timeout=120
            )

            response.raise_for_status()

            results = response.json()
            errors = [item for item in results if "error" in item]

            if errors:
                print("Some documents failed to upload:")
                print(errors[:5])
                raise SystemExit

            uploaded += len(batch)
            print("Invoices uploaded:", uploaded)

            batch = []

    # Upload remaining invoices
    if batch:

        response = requests.post(
            f"{database_url}/_bulk_docs",
            auth=(username, password),
            json={"docs": batch},
            timeout=120
        )

        response.raise_for_status()

        results = response.json()
        errors = [item for item in results if "error" in item]

        if errors:
            print("Some documents failed to upload:")
            print(errors[:5])
            raise SystemExit

        uploaded += len(batch)

    # Verify upload
    verification = requests.get(
        database_url,
        auth=(username, password),
        timeout=30
    )

    verification.raise_for_status()

    print("\n========== UPLOAD SUMMARY ==========")
    print("Transaction rows:", len(df))
    print("Invoice documents uploaded:", uploaded)
    print(
        "Cloudant document count:",
        verification.json().get("doc_count")
    )

    print("\nTransaction data uploaded successfully!")

except requests.exceptions.RequestException as error:
    print("Cloudant upload error:", error)

print("\n========== UPLOAD PROCESS COMPLETED ==========")
