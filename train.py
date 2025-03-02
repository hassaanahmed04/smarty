import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler

# Load historic data
df = pd.read_csv('tvws_historical_data.csv', parse_dates=['date'])

# Ensure the 'date' column is in datetime format
df['date'] = pd.to_datetime(df['date'])

# Setting 'date' as the index
df.set_index('date', inplace=True)

# Handle missing values by filling forward (you can choose other methods like interpolation)
df.fillna(method='ffill', inplace=True)

# --- 1. Time-Series Forecasting for Interference Trends ---
# Predict Interference Level based on time-series data
def predict_interference(df):
    # Group by Cluster and predict for each cluster
    interference_predictions = {}
    for cluster in df['Cluster'].unique():
        cluster_data = df[df['Cluster'] == cluster]
        
        # We will use the 'Interference Level' as the target variable
        cluster_data['Interference Level'] = cluster_data['Interference Level'].map({'Low': 0, 'Medium': 1, 'High': 2})  # Convert categorical to numerical
        
        # Train ARIMA model on 'Interference Level'
        model = ARIMA(cluster_data['Interference Level'], order=(5, 1, 0))  # You can adjust ARIMA order based on your data
        model_fit = model.fit()

        # Forecast the next 10 periods (e.g., months or days)
        forecast = model_fit.forecast(steps=10)
        
        interference_predictions[cluster] = forecast
    return interference_predictions

interference_predictions = predict_interference(df)
print(f"Interference Predictions: {interference_predictions}")

# --- 2. Predicting Failure Rate Using Random Forest ---
# For failure rate prediction, we use relevant features like temperature, humidity, and spectrum utilization.
def predict_failure_rate(df):
    # Define target (Failure Rate) and features (Temperature, Humidity, Spectrum Utilization)
    X = df[['Temperature (°C)', 'Humidity (%)', 'Spectrum Utilization (%)']]
    y = df['Failure Rate (%)']
    
    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a Random Forest model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # Predict on the test set
    y_pred = rf.predict(X_test)
    
    # Calculate the Mean Absolute Error (MAE)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE for Failure Rate Prediction: {mae}")
    
    # Feature importance
    feature_importance = rf.feature_importances_
    feature_names = X.columns
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    }).sort_values(by='Importance', ascending=False)
    
    print("Feature Importance (Critical factors for failure prediction):")
    print(feature_importance_df)
    
    return rf, y_pred

rf_model, failure_rate_predictions = predict_failure_rate(df)

# --- 3. Visualize the Forecast and Predictions ---
import matplotlib.pyplot as plt

# Visualizing Interference Predictions (for the first cluster as an example)
def plot_interference_forecast(interference_predictions):
    plt.figure(figsize=(10, 6))
    
    for cluster, forecast in interference_predictions.items():
        plt.plot(forecast, label=f"Cluster {cluster}")
    
    plt.title("Interference Forecast")
    plt.xlabel("Time (Next 10 periods)")
    plt.ylabel("Predicted Interference Level")
    plt.legend()
    plt.show()

plot_interference_forecast(interference_predictions)

# Visualize Failure Rate Predictions
def plot_failure_rate_predictions(y_test, y_pred):
    plt.figure(figsize=(10, 6))
    plt.plot(y_test.values, label="Actual Failure Rate")
    plt.plot(y_pred, label="Predicted Failure Rate", linestyle="--")
    plt.title("Failure Rate Prediction")
    plt.xlabel("Index")
    plt.ylabel("Failure Rate (%)")
    plt.legend()
    plt.show()

plot_failure_rate_predictions(y_test, failure_rate_predictions)
