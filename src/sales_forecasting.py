
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

print("========== SMARTRETAIL SALES FORECASTING ==========")

# 1. Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_retail.csv")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# 2. Calculate daily revenue
df["InvoiceDay"] = df["InvoiceDate"].dt.normalize()
daily_sales = df.groupby("InvoiceDay")["Revenue"].sum()

all_dates = pd.date_range(
    start=daily_sales.index.min(),
    end=daily_sales.index.max(),
    freq="D"
)

daily_sales = daily_sales.reindex(all_dates, fill_value=0)
daily_sales.index.name = "Date"

# 3. Create training features
features = [
    "DayOfWeek",
    "Day",
    "Month",
    "DayOfYear",
    "Lag_1",
    "Lag_7",
    "Rolling_7"
]

records = []

for i in range(7, len(daily_sales)):

    date = daily_sales.index[i]
    history = daily_sales.iloc[:i]

    records.append({
        "Date": date,
        "DayOfWeek": date.day_of_week,
        "Day": date.day,
        "Month": date.month,
        "DayOfYear": date.day_of_year,
        "Lag_1": history.iloc[-1],
        "Lag_7": history.iloc[-7],
        "Rolling_7": history.iloc[-7:].mean(),
        "Revenue": daily_sales.iloc[i]
    })

data = pd.DataFrame(records).set_index("Date")

X = data[features]
y = data["Revenue"]

# 4. Split historical data into training and testing
test_start = data.index.max() - pd.Timedelta(days=29)

X_train = X[data.index < test_start]
y_train = y[data.index < test_start]

test_dates = data.index[data.index >= test_start]
y_test = y.loc[test_dates]

# 5. Train model for evaluation
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    min_samples_leaf=2
)

model.fit(X_train, y_train)

# 6. Recursive 30-day testing
history = list(daily_sales.loc[
    daily_sales.index < test_start
].values)

test_predictions = []

for date in test_dates:

    input_data = pd.DataFrame([{
        "DayOfWeek": date.day_of_week,
        "Day": date.day,
        "Month": date.month,
        "DayOfYear": date.day_of_year,
        "Lag_1": history[-1],
        "Lag_7": history[-7],
        "Rolling_7": np.mean(history[-7:])
    }])

    prediction = model.predict(input_data)[0]
    prediction = max(0, prediction)

    test_predictions.append(prediction)
    history.append(prediction)

# 7. Evaluate model
mae = mean_absolute_error(y_test, test_predictions)
rmse = np.sqrt(mean_squared_error(y_test, test_predictions))

print("\n1. MODEL EVALUATION")
print("Training records:", len(X_train))
print("Testing records:", len(y_test))
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))

# 8. Train final model using all historical data
final_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    min_samples_leaf=2
)

final_model.fit(X, y)

# 9. Forecast next 30 days
history = list(daily_sales.values)
last_date = daily_sales.index.max()

forecast_results = []

for i in range(1, 31):

    future_date = last_date + pd.Timedelta(days=i)

    input_data = pd.DataFrame([{
        "DayOfWeek": future_date.day_of_week,
        "Day": future_date.day,
        "Month": future_date.month,
        "DayOfYear": future_date.day_of_year,
        "Lag_1": history[-1],
        "Lag_7": history[-7],
        "Rolling_7": np.mean(history[-7:])
    }])

    prediction = final_model.predict(input_data)[0]
    prediction = max(0, prediction)

    forecast_results.append({
        "Date": future_date,
        "PredictedRevenue": round(prediction, 2)
    })

    history.append(prediction)

forecast_df = pd.DataFrame(forecast_results)

# 10. Create output folders
os.makedirs("reports/forecasting", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Save forecast
forecast_df.to_csv(
    "reports/forecasting/sales_forecast.csv",
    index=False
)

# Save model
with open("models/sales_forecasting_model.pkl", "wb") as file:
    pickle.dump(final_model, file)

# 11. Display forecast
print("\n2. NEXT 30 DAYS SALES FORECAST")
print(forecast_df.to_string(index=False))

print("\n3. FORECAST SUMMARY")
print(
    "Total predicted revenue: £",
    round(forecast_df["PredictedRevenue"].sum(), 2)
)

print(
    "Average predicted daily revenue: £",
    round(forecast_df["PredictedRevenue"].mean(), 2)
)

# 12. Compare actual and predicted test sales
plt.figure(figsize=(12, 6))

plt.plot(
    y_test.index,
    y_test.values,
    label="Actual Revenue"
)

plt.plot(
    y_test.index,
    test_predictions,
    label="Predicted Revenue",
    linestyle="--"
)

plt.title("Actual vs Predicted Sales - Test Period")
plt.xlabel("Date")
plt.ylabel("Revenue (£)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("reports/forecasting/model_evaluation.png")
plt.close()

# 13. Forecast chart
plt.figure(figsize=(12, 6))

plt.plot(
    daily_sales.index[-60:],
    daily_sales.values[-60:],
    label="Historical Revenue"
)

plt.plot(
    forecast_df["Date"],
    forecast_df["PredictedRevenue"],
    label="Future Forecast",
    linestyle="--",
    marker="o"
)

plt.title("30-Day Retail Sales Forecast")
plt.xlabel("Date")
plt.ylabel("Revenue (£)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("reports/forecasting/sales_forecast.png")
plt.close()

print("\nForecast, model and evaluation chart saved successfully!")
print("\n========== FORECASTING COMPLETED ==========")
