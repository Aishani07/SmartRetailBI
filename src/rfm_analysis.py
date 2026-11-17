
import pandas as pd
import os

print("========== SMARTRETAIL CUSTOMER INTELLIGENCE ==========")

# Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_retail.csv")

# Convert invoice date
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Remove records without CustomerID for customer analysis
customer_df = df.dropna(subset=["CustomerID"]).copy()

# Reference date: one day after the last transaction
reference_date = customer_df["InvoiceDate"].max() + pd.Timedelta(days=1)

# Calculate RFM values for each customer
rfm = customer_df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()

# Create RFM scores
# Recency: lower number of days is better
rfm["R_Score"] = pd.qcut(
    rfm["Recency"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)

# Frequency: more purchases is better
rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Monetary: higher spending is better
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Calculate total RFM score
rfm["RFM_Score"] = (
    rfm["R_Score"] +
    rfm["F_Score"] +
    rfm["M_Score"]
)

# Assign customer segments
def assign_segment(row):

    r = row["R_Score"]
    f = row["F_Score"]
    m = row["M_Score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    elif r >= 3 and f >= 4:
        return "Loyal Customers"

    elif r >= 4 and f >= 2:
        return "Potential Loyalists"

    elif r <= 2 and f >= 3:
        return "At Risk"

    elif r <= 2 and f <= 2:
        return "Needs Attention"

    else:
        return "Regular Customers"


rfm["CustomerSegment"] = rfm.apply(assign_segment, axis=1)

# Create output folder
os.makedirs("reports/customer_analysis", exist_ok=True)

# Save individual customer RFM data
rfm.to_csv(
    "reports/customer_analysis/customer_segments.csv",
    index=False
)

# Segment summary
segment_summary = rfm.groupby("CustomerSegment").agg(
    CustomerCount=("CustomerID", "count"),
    AverageMonetary=("Monetary", "mean"),
    TotalRevenue=("Monetary", "sum")
).reset_index()

segment_summary = segment_summary.sort_values(
    by="CustomerCount",
    ascending=False
)

segment_summary.to_csv(
    "reports/customer_analysis/segment_summary.csv",
    index=False
)

# Display results
print("\n1. TOTAL CUSTOMERS ANALYSED")
print(len(rfm))

print("\n2. CUSTOMER RFM DETAILS")
print(rfm.head(10).to_string(index=False))

print("\n3. CUSTOMER SEGMENT SUMMARY")
print(segment_summary.to_string(index=False))

print("\n4. HIGHEST VALUE CUSTOMERS")
print(
    rfm.sort_values(
        by="Monetary",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\nRFM analysis completed successfully!")
print("Files saved in reports/customer_analysis/")

print("\n========== CUSTOMER INTELLIGENCE COMPLETED ==========")
