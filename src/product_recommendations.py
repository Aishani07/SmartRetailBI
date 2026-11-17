
import pandas as pd
import os
from itertools import combinations
from collections import Counter

print("========== SMARTRETAIL PRODUCT RECOMMENDATIONS ==========")

# Load cleaned dataset
df = pd.read_csv(
    "data/processed/cleaned_retail.csv",
    low_memory=False
)

# Convert product codes and descriptions to consistent text
df["StockCode"] = df["StockCode"].astype(str)
df["Description"] = df["Description"].fillna("Unknown Product").str.strip()

# Exclude postage and adjustment entries
excluded_words = (
    "POSTAGE",
    "DOTCOM",
    "MANUAL",
    "BANK CHARGES",
    "CARRIAGE",
    "COMMISSION",
    "FEE"
)

df = df[
    ~df["Description"].str.upper().str.contains(
        "|".join(excluded_words),
        regex=True
    )
]

# Get one product name for each product code
product_names = (
    df.groupby("StockCode")["Description"]
    .agg(lambda x: x.value_counts().index[0])
    .to_dict()
)

# Get unique products purchased in each invoice
invoice_products = (
    df.groupby("InvoiceNo")["StockCode"]
    .apply(lambda x: sorted(set(x)))
)

# Count how many invoices contain each product
product_invoice_count = Counter()

# Count how often two products appear together
pair_counts = Counter()

for products in invoice_products:

    product_invoice_count.update(products)

    if len(products) >= 2:
        for pair in combinations(products, 2):
            pair_counts[pair] += 1

total_invoices = len(invoice_products)

# Create product pair analysis
pair_results = []

for (product_a, product_b), count in pair_counts.items():

    pair_results.append({
        "Product A": product_names.get(product_a, "Unknown"),
        "Product B": product_names.get(product_b, "Unknown"),
        "CoPurchaseCount": count,
        "Support": round(count / total_invoices, 4)
    })

pair_df = pd.DataFrame(pair_results)

# Create recommendations in both directions
recommendation_results = []

for (product_a, product_b), count in pair_counts.items():

    confidence_a = count / product_invoice_count[product_a]
    confidence_b = count / product_invoice_count[product_b]

    recommendation_results.append({
        "Product": product_names.get(product_a, "Unknown"),
        "RecommendedProduct": product_names.get(product_b, "Unknown"),
        "CoPurchaseCount": count,
        "Confidence": round(confidence_a, 4)
    })

    recommendation_results.append({
        "Product": product_names.get(product_b, "Unknown"),
        "RecommendedProduct": product_names.get(product_a, "Unknown"),
        "CoPurchaseCount": count,
        "Confidence": round(confidence_b, 4)
    })

recommendations_df = pd.DataFrame(recommendation_results)

# Keep pairs found in at least two invoices
recommendations_df = recommendations_df[
    recommendations_df["CoPurchaseCount"] >= 5
]

# Sort recommendations by confidence and co-purchase count
recommendations_df = recommendations_df.sort_values(
    by=["Product", "Confidence", "CoPurchaseCount"],
    ascending=[True, False, False]
)

# Keep the top five recommendations for each product
top_recommendations = (
    recommendations_df.groupby("Product")
    .head(5)
    .reset_index(drop=True)
)

# Create output folder
output_folder = "reports/product_recommendations"
os.makedirs(output_folder, exist_ok=True)

# Save results
pair_df.to_csv(
    os.path.join(output_folder, "product_pair_analysis.csv"),
    index=False
)

top_recommendations.to_csv(
    os.path.join(output_folder, "product_recommendations.csv"),
    index=False
)

# Display summary
print("\n1. RECOMMENDATION SYSTEM SUMMARY")

print("Total invoices analysed:", total_invoices)
print("Unique products analysed:", len(product_invoice_count))
print("Product pairs identified:", len(pair_counts))
print("Products with recommendations:", top_recommendations["Product"].nunique())

print("\n2. TOP PRODUCT RECOMMENDATIONS")

if len(top_recommendations) > 0:
    print(top_recommendations.head(15).to_string(index=False))
else:
    print("No product recommendations found.")

print("\n3. OUTPUT FILES SAVED")
print("Product pair analysis: product_pair_analysis.csv")
print("Product recommendations: product_recommendations.csv")

print("\n========== PRODUCT RECOMMENDATIONS COMPLETED ==========")
