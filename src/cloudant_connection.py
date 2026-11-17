
import os
import requests
from dotenv import load_dotenv

print("========== SMARTRETAIL CLOUDANT CONNECTION ==========")

# Load credentials from .env
load_dotenv()

cloudant_url = os.getenv("CLOUDANT_URL")
username = os.getenv("CLOUDANT_USERNAME")
password = os.getenv("CLOUDANT_PASSWORD")

# Check whether credentials are available
if not cloudant_url or not username or not password:
    print("Cloudant credentials are missing.")
else:
    try:
        response = requests.get(
            cloudant_url,
            auth=(username, password),
            timeout=20
        )

        if response.status_code == 200:
            print("Cloudant connection successful!")
            print("Database server is accessible.")

        else:
            print("Connection failed.")
            print("Status code:", response.status_code)
            print("Please check your credentials and URL.")

    except requests.exceptions.RequestException as error:
        print("Unable to connect to Cloudant.")
        print("Error:", error)

print("========== CONNECTION TEST COMPLETED ==========")
