
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

print("========== SMARTRETAIL INTELLIGENCE API ==========")

# Load analytics datasets
sales = pd.read_csv("reports/eda/tables/monthly_sales.csv")
countries = pd.read_csv("reports/eda/tables/country_sales.csv")
customers = pd.read_csv("reports/customer_analysis/customer_segments.csv")
forecasts = pd.read_csv("reports/forecasting/sales_forecast.csv")
anomalies = pd.read_csv("reports/anomaly_detection/sales_anomalies.csv")
recommendations = pd.read_csv(
    "reports/product_recommendations/product_recommendations.csv"
)


# HOME API
@app.route("/")
def home():
    return jsonify({
        "project": "SmartRetail Intelligence",
        "message": "API is running successfully"
    })


# SALES SUMMARY API
@app.route("/api/sales")
def sales_summary():
    return jsonify({
        "total_revenue": round(float(sales["Revenue"].sum()), 2),
        "months_analysed": len(sales)
    })


# MONTHLY SALES API
@app.route("/api/monthly-sales")
def monthly_sales():
    return jsonify(sales.to_dict(orient="records"))


# COUNTRY-WISE SALES API
@app.route("/api/countries")
def country_summary():
    result = countries.sort_values(
        "Revenue", ascending=False
    ).head(10)

    return jsonify(result.to_dict(orient="records"))


# CUSTOMER SUMMARY API
@app.route("/api/customers")
def customer_summary():
    result = customers.sort_values(
        "Monetary", ascending=False
    ).head(10)

    return jsonify(result.to_dict(orient="records"))


# CUSTOMER SEGMENTATION API
@app.route("/api/segments")
def segment_summary():
    summary = customers.groupby("CustomerSegment").agg(
        CustomerCount=("CustomerID", "count"),
        TotalRevenue=("Monetary", "sum")
    ).reset_index()

    return jsonify(summary.to_dict(orient="records"))


# SALES FORECAST API
@app.route("/api/forecast")
def sales_forecast():
    return jsonify(forecasts.to_dict(orient="records"))


# SALES ANOMALY API
@app.route("/api/anomalies")
def sales_anomalies():
    return jsonify(anomalies.to_dict(orient="records"))


# PRODUCT RECOMMENDATIONS API
@app.route("/api/recommendations")
def product_recommendations():
    product = request.args.get("product", "").strip()

    if not product:
        return jsonify({
            "message": "Please provide a product name."
        }), 400

    result = recommendations[
        recommendations["Product"].str.contains(
            product,
            case=False,
            na=False,
            regex=False
        )
    ]

    result = result.sort_values(
        "CoPurchaseCount", ascending=False
    ).head(5)

    return jsonify(result.to_dict(orient="records"))

# SMARTRETAIL AI CHATBOT API
@app.route("/api/chat", methods=["POST"])
def chatbot():

    data = request.get_json()
    question = data.get("question", "").strip().lower()

    if not question:
        return jsonify({"answer": "Please enter a question."}), 400

    # TOTAL REVENUE
    if "revenue" in question or "total sales" in question:
        total = sales["Revenue"].sum()

        answer = (
            f"The total revenue recorded in the dataset is "
            f"£{total:,.2f}."
        )

    # TOP COUNTRIES
    elif "country" in question or "countries" in question:
        top = countries.sort_values(
            "Revenue", ascending=False
        ).head(5)

        answer = "Top 5 countries by revenue:\n"

        for _, row in top.iterrows():
            answer += (
                f"\n{row['Country']}: £{row['Revenue']:,.2f}"
            )

    # TOP CUSTOMERS
    elif "top customer" in question or "best customer" in question:
        top = customers.sort_values(
            "Monetary", ascending=False
        ).head(5)

        answer = "Top 5 customers by revenue:\n"

        for _, row in top.iterrows():
            answer += (
                f"\nCustomer {row['CustomerID']}: "
                f"£{row['Monetary']:,.2f}"
            )

    # CUSTOMER SEGMENTS
    elif "segment" in question or "customer group" in question:
        summary = customers.groupby("CustomerSegment").agg(
            CustomerCount=("CustomerID", "count"),
            TotalRevenue=("Monetary", "sum")
        ).reset_index()

        answer = "Customer segmentation summary:\n"

        for _, row in summary.iterrows():
            answer += (
                f"\n{row['CustomerSegment']}: "
                f"{int(row['CustomerCount'])} customers"
            )

    # SALES FORECAST
    elif "forecast" in question or "future sales" in question:
        total_forecast = forecasts["PredictedRevenue"].sum()
        average_forecast = forecasts["PredictedRevenue"].mean()

        answer = (
            f"The 30-day historical-model forecast is "
            f"£{total_forecast:,.2f} in total, with an "
            f"average daily forecast of £{average_forecast:,.2f}."
        )

    # SALES ANOMALIES
    elif "anomal" in question or "unusual sales" in question:
        answer = (
            f"The anomaly detection system identified "
            f"{len(anomalies)} unusual sales days."
        )

    # PRODUCT RECOMMENDATIONS
    elif "recommend" in question or "product" in question:
        answer = (
            "Please use the Product Recommendations search "
            "section to enter a product name and see related products."
        )

    # HELP
    elif "help" in question:
        answer = (
            "You can ask me about total revenue, top countries, "
            "top customers, customer segments, sales forecasts "
            "and sales anomalies."
        )

    else:
        answer = (
            "I could not understand that question. "
            "Try asking about revenue, customers, countries, "
            "segments, forecasts or anomalies."
        )

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
