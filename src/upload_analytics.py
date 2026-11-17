
import os
import requests
import pandas as pd
from dotenv import load_dotenv

print("========== SMARTRETAIL ANALYTICS UPLOAD ==========")

load_dotenv()

cloudant_url = os.getenv("CLOUDANT_URL").rstrip("/")
username = os.getenv("CLOUDANT_USERNAME")
password = os.getenv("CLOUDANT_PASSWORD")

database_url = f"{cloudant_url}/smartretail"

# Files to upload and their document types
files = [
    ("reports/customer_analysis/customer_segments.csv", "customer_segment"),
    ("reports/customer_analysis/segment_summary.csv", "segment_summary"),
    ("reports/forecasting/sales_forecast.csv", "sales_forecast"),
    ("reports/anomaly_detection/sales_anomalies.csv", "sales_anomaly"),
    ("reports/product_recommendations/product_recommendations.csv", "product_recommendation")
]

def upload_records(file_path, document_type):

    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return

    df = pd.read_csv(file_path, low_memory=False)

    documents = []

    for index, row in df.iterrows():

        document = row.where(pd.notna(row), None).to_dict()

        # Convert NumPy values into normal Python values
        document = {
            key: value.item() if hasattr(value, "item") else value
            for key, value in document.items()
        }

        document["_id"] = f"{document_type}_{index}"
        document["document_type"] = document_type

        documents.append(document)

    if not documents:
        print(document_type, ": No records to upload.")
        return

    # Check which documents already exist
    ids = [doc["_id"] for doc in documents]
    existing_ids = set()

    for start in range(0, len(ids), 500):

        id_batch = ids[start:start + 500]

        response = requests.post(
            f"{database_url}/_all_docs",
            auth=(username, password),
            json={"keys": id_batch},
            timeout=60
        )

        response.raise_for_status()

        for item in response.json()["rows"]:
            if item.get("value"):
                existing_ids.add(item["id"])

    # Upload only new documents
    new_documents = [
        doc for doc in documents
        if doc["_id"] not in existing_ids
    ]

    uploaded = 0

    for start in range(0, len(new_documents), 500):

        batch = new_documents[start:start + 500]

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
            print("Upload errors:", errors[:5])
            raise Exception("Some documents could not be uploaded.")

        uploaded += len(batch)

    print(
        document_type,
        "- Total:", len(documents),
        "| Newly uploaded:", uploaded,
        "| Already present:", len(existing_ids)
    )


try:

    for file_path, document_type in files:
        upload_records(file_path, document_type)

    # Verify final database count
    response = requests.get(
        database_url,
        auth=(username, password),
        timeout=30
    )

    response.raise_for_status()

    print("\nFinal Cloudant document count:",
          response.json().get("doc_count"))

    print("\nAll analytics results uploaded successfully!")

except Exception as error:
    print("\nUpload failed:", error)

print("\n========== ANALYTICS UPLOAD COMPLETED ==========")
