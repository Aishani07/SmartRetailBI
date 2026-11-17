
import pandas as pd
import os

# Dataset location
file_path = "data/raw/Online Retail.xlsx"

# Check whether the file exists
if not os.path.exists(file_path):
    print("Dataset file not found. Check the file location.")
else:
    # Load Excel dataset
    df = pd.read_excel(file_path)

    print("\n========== SMARTRETAIL INTELLIGENCE ==========")
    print("\n1. DATASET LOADED SUCCESSFULLY")

    # Display number of rows and columns
    print("\n2. DATASET SIZE")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    # Display column names
    print("\n3. COLUMN NAMES")
    print(df.columns.tolist())

    # Display first five records
    print("\n4. FIRST FIVE RECORDS")
    print(df.head())

    # Display data types
    print("\n5. DATA TYPES")
    print(df.dtypes)

    # Check missing values
    print("\n6. MISSING VALUES")
    print(df.isnull().sum())

    # Check duplicate records
    print("\n7. DUPLICATE RECORDS")
    print(df.duplicated().sum())

    print("\n========== INSPECTION COMPLETED ==========")
