
import pandas as pd
import matplotlib.pyplot as plt
import os

print("========== SMARTRETAIL EXPLORATORY DATA ANALYSIS ==========")

# Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_retail.csv")

# Convert date column
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Create output folders
os.makedirs("reports/eda/charts", exist_ok=True)
os.makedirs("reports/eda/tables", exist_ok=True)

# 1. Overall sales performance
total_revenue = df["Revenue"].sum()
total_transactions = df["InvoiceNo"].nunique()
total_products = df["StockCode"].nunique()
total_countries = df["Country"].nunique()
total_customers = df["CustomerID"].nunique()

print("\n1. OVERALL SALES PERFORMANCE")
print("Total Revenue: £", round(total_revenue, 2))
print("Total Transactions:", total_transactions)
print("Unique Products:", total_products)
print("Countries:", total_countries)
print("Unique Customers:", total_customers)

# 2. Top 10 products by revenue
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

print("\n2. TOP 10 PRODUCTS BY REVENUE")
print(top_products)

top_products.to_csv(
    "reports/eda/tables/top_products.csv", index=False
)

# Product chart
plt.figure(figsize=(12, 6))
plt.barh(top_products["Description"], top_products["Revenue"])
plt.xlabel("Revenue (£)")
plt.ylabel("Product")
plt.title("Top 10 Products by Revenue")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("reports/eda/charts/top_products.png")
plt.close()

# 3. Top 10 countries by revenue
country_sales = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

print("\n3. TOP 10 COUNTRIES BY REVENUE")
print(country_sales)

country_sales.to_csv(
    "reports/eda/tables/country_sales.csv", index=False
)

# Country chart
plt.figure(figsize=(10, 6))
plt.bar(country_sales["Country"], country_sales["Revenue"])
plt.xlabel("Country")
plt.ylabel("Revenue (£)")
plt.title("Top 10 Countries by Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/eda/charts/country_sales.png")
plt.close()

# 4. Monthly sales trends
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

monthly_sales = (
    df.groupby("Month")["Revenue"]
    .sum()
    .reset_index()
)

print("\n4. MONTHLY SALES")
print(monthly_sales)

monthly_sales.to_csv(
    "reports/eda/tables/monthly_sales.csv", index=False
)

# Monthly sales chart
plt.figure(figsize=(12, 6))
plt.plot(
    monthly_sales["Month"],
    monthly_sales["Revenue"],
    marker="o"
)
plt.xlabel("Month")
plt.ylabel("Revenue (£)")
plt.title("Monthly Revenue Trend")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/eda/charts/monthly_sales.png")
plt.close()

# 5. Customer performance
customer_sales = (
    df.dropna(subset=["CustomerID"])
    .groupby("CustomerID")
    .agg(
        TotalRevenue=("Revenue", "sum"),
        TotalOrders=("InvoiceNo", "nunique"),
        TotalQuantity=("Quantity", "sum")
    )
    .reset_index()
)

top_customers = customer_sales.sort_values(
    by="TotalRevenue", ascending=False
).head(10)

print("\n5. TOP 10 CUSTOMERS BY REVENUE")
print(top_customers)

top_customers.to_csv(
    "reports/eda/tables/top_customers.csv", index=False
)

# Customer chart
plt.figure(figsize=(10, 6))
plt.bar(
    top_customers["CustomerID"].astype(str),
    top_customers["TotalRevenue"]
)
plt.xlabel("Customer ID")
plt.ylabel("Revenue (£)")
plt.title("Top 10 Customers by Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/eda/charts/top_customers.png")
plt.close()

print("\nAll analysis tables and charts saved successfully!")
print("Location: reports/eda/")

print("\n========== EDA COMPLETED ==========")
