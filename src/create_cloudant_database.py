
import os
import requests
from dotenv import load_dotenv

print("========== SMARTRETAIL DATABASE SETUP ==========")

load_dotenv()

cloudant_url = os.getenv("CLOUDANT_URL").rstrip("/")
username = os.getenv("CLOUDANT_USERNAME")
password = os.getenv("CLOUDANT_PASSWORD")

database_name = "smartretail"

try:
    response = requests.put(
        f"{cloudant_url}/{database_name}",
        auth=(username, password),
        timeout=30
    )

    if response.status_code == 201:
        print("Database created successfully!")

    elif response.status_code == 412:
        print("Database already exists. We can use it.")

    else:
        print("Database creation failed.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

    # Verify database
    check = requests.get(
        f"{cloudant_url}/{database_name}",
        auth=(username, password),
        timeout=30
    )

    if check.status_code == 200:
        details = check.json()
        print("\nDATABASE DETAILS")
        print("Database name:", details.get("db_name"))
        print("Document count:", details.get("doc_count"))
        print("\nCloudant database is ready!")

except requests.exceptions.RequestException as error:
    print("Error connecting to Cloudant:", error)

print("\n========== DATABASE SETUP COMPLETED ==========")
