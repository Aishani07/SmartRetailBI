
import pandas as pd
import os

print("========== SMARTRETAIL DATA CLEANING ==========")

# Load original dataset
file_path = "data/raw/Online Retail.xlsx"
df = pd.read_excel(file_path)

print("\nOriginal number of rows:", len(df))

# Step 1: Remove duplicate records
df = df.drop_duplicates()
print("After removing duplicates:", len(df))

# Step 2: Fill missing product descriptions
df["Description"] = df["Description"].fillna("Unknown Product")

# Step 3: Identify cancelled invoices
cancelled = df["InvoiceNo"].astype(str).str.startswith("C")
print("Cancelled invoice records:", cancelled.sum())

# Remove cancelled invoices
df = df[~cancelled]

# Step 4: Remove invalid quantities
invalid_quantity = df["Quantity"] <= 0
print("Records with invalid quantity:", invalid_quantity.sum())
df = df[~invalid_quantity]

# Step 5: Remove invalid unit prices
invalid_price = df["UnitPrice"] <= 0
print("Records with invalid unit price:", invalid_price.sum())
df = df[~invalid_price]

# Step 6: Create Revenue column
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# Step 7: Create additional date columns
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["Date"] = df["InvoiceDate"].dt.date

# Step 8: Save cleaned dataset
output_folder = "data/processed"
os.makedirs(output_folder, exist_ok=True)

output_file = os.path.join(output_folder, "cleaned_retail.csv")
df.to_csv(output_file, index=False)

# Display final results
print("\n========== CLEANING SUMMARY ==========")
print("Final number of rows:", len(df))
print("Final number of columns:", len(df.columns))
print("Missing Customer IDs:", df["CustomerID"].isnull().sum())
print("Missing descriptions:", df["Description"].isnull().sum())
print("Total Revenue: £", round(df["Revenue"].sum(), 2))

print("\nCleaned dataset saved successfully!")
print("File location:", output_file)

print("\n========== CLEANING COMPLETED ==========")
