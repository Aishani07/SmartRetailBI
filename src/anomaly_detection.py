
import pandas as pd
import matplotlib.pyplot as plt
import os

print("========== SMARTRETAIL ANOMALY DETECTION ==========")

# Load cleaned dataset
df = pd.read_csv(
    "data/processed/cleaned_retail.csv",
    low_memory=False
)

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Calculate daily revenue
daily_sales = df.groupby(
    df["InvoiceDate"].dt.date
)["Revenue"].sum()

# Include dates with zero sales
daily_sales.index = pd.to_datetime(daily_sales.index)

date_range = pd.date_range(
    start=daily_sales.index.min(),
    end=daily_sales.index.max(),
    freq="D"
)

daily_sales = daily_sales.reindex(
    date_range,
    fill_value=0
)

sales_df = pd.DataFrame({
    "Date": daily_sales.index,
    "Revenue": daily_sales.values
})

# Identify weekday for comparison
sales_df["Weekday"] = sales_df["Date"].dt.day_name()

# Calculate anomaly limits separately for each weekday
sales_df["LowerLimit"] = 0.0
sales_df["UpperLimit"] = 0.0

for weekday in sales_df["Weekday"].unique():

    mask = sales_df["Weekday"] == weekday

    values = sales_df.loc[mask, "Revenue"]

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower_limit = max(0, q1 - 1.5 * iqr)
    upper_limit = q3 + 1.5 * iqr

    sales_df.loc[mask, "LowerLimit"] = lower_limit
    sales_df.loc[mask, "UpperLimit"] = upper_limit

# Mark unusual sales days
sales_df["Anomaly"] = (
    (sales_df["Revenue"] < sales_df["LowerLimit"]) |
    (sales_df["Revenue"] > sales_df["UpperLimit"])
)

anomalies = sales_df[sales_df["Anomaly"]].copy()

# Classify anomalies
anomalies["AnomalyType"] = anomalies.apply(
    lambda row: "Unusually High Sales"
    if row["Revenue"] > row["UpperLimit"]
    else "Unusually Low Sales",
    axis=1
)

# Create output folders
output_folder = "reports/anomaly_detection"
os.makedirs(output_folder, exist_ok=True)

# Save anomaly records
anomalies.to_csv(
    os.path.join(output_folder, "sales_anomalies.csv"),
    index=False
)

# Print results
print("\n1. ANOMALY DETECTION SUMMARY")

print("Total days analysed:", len(sales_df))
print("Total anomalies detected:", len(anomalies))

print("\n2. DETECTED ANOMALIES")

if len(anomalies) > 0:
    print(
        anomalies[
            ["Date", "Revenue", "Weekday", "AnomalyType"]
        ].to_string(index=False)
    )
else:
    print("No unusual sales days detected.")

# Plot sales and anomalies
plt.figure(figsize=(14, 6))

plt.plot(
    sales_df["Date"],
    sales_df["Revenue"],
    label="Daily Revenue"
)

if len(anomalies) > 0:
    plt.scatter(
        anomalies["Date"],
        anomalies["Revenue"],
        label="Detected Anomalies"
    )

plt.title("SmartRetail - Sales Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Revenue (£)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "sales_anomalies.png")
)

plt.close()

print("\nAnomaly report and chart saved successfully!")
print("Output folder:", output_folder)

print("\n========== ANOMALY DETECTION COMPLETED ==========")
