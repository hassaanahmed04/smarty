# /app/functions.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
import subprocess
import json
# Load the historic data
def load_data():
    df = pd.read_csv('dataset/tvws_historical_data.csv', parse_dates=['date'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df


# --- Time-Series Forecasting for Interference Trends ---
def predict_interference(df):
    interference_predictions = {}
    for cluster in df['Cluster'].unique():
        cluster_data = df[df['Cluster'] == cluster]
        cluster_data['Interference Level'] = cluster_data['Interference Level'].map({'Low': 0, 'Medium': 1, 'High': 2})
        
        # Train ARIMA model on 'Interference Level'
        model = ARIMA(cluster_data['Interference Level'], order=(5, 1, 0))
        model_fit = model.fit()

        forecast = model_fit.forecast(steps=10)
        
        # Convert forecast (which is a numpy array or pandas Series) to list
        interference_predictions[cluster] = forecast.tolist()
    
    return interference_predictions


# --- Predicting Failure Rate Using Random Forest ---
def predict_failure_rate(df, station_name):
    # Select relevant features and target variable
    X = df[['Temperature (°C)', 'Humidity (%)', 'Spectrum Utilization (%)', 'Signal Strength (dBm)', 
            'Elevation', 'Population', 'TVWS Range (km)']]
    y = df['Failure Rate (%)']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a Random Forest Regressor model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # Predict failure rates on the test set
    y_pred = rf.predict(X_test)
    
    # Calculate the Mean Absolute Error (MAE)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Get feature importance to identify key causes of failure
    feature_importance = rf.feature_importances_
    feature_names = X.columns
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    }).sort_values(by='Importance', ascending=False)
    
    # Get the predicted failure rate for the first station (or adjust based on your needs)
    failure_rate = y_pred[0]
    
    # Select the top 5 features with the highest importance
    important_features = feature_importance_df[['Feature', 'Importance']].head(5).values.tolist()
    
    # Construct prompt based on failure prediction and feature importance
    prompt = f"""
    We have the following TVWS station failure prediction:

    - Station: {station_name}
    - Predicted Failure Rate: {failure_rate:.2f}%
    - Key Factors: 
    """
    
    for feature, importance in important_features:
        impact = "High" if importance > 0.2 else "Moderate"
        prompt += f"    - {feature}: {impact} impact ({importance:.2f} importance)\n"
    
    prompt += """
    Given these conditions, please provide the following recommendations:

    1. **Maintenance Actions:** What proactive maintenance steps should be taken to prevent failure, considering the major risk factors like Signal Strength, Temperature, and Humidity?
    2. **Precautions:** What precautions should be taken to mitigate the effects of high spectrum utilization or other environmental factors?
    3. **Best Practices:** Based on this information, what long-term maintenance practices should be implemented to ensure reliability for this station?
    4. **Immediate Fixes:** Is there any immediate action required to reduce the failure probability in the short term?
    """

    # Prepare the JSON payload for Gemini API
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    # Replace with your actual Gemini API key
    GEMINI_API_KEY = "AIzaSyDOWE8puOkL2Nv0TxofKoRBjhvdzxlCKbg"

    # Call the Gemini API and get the response
    response = call_gemini_api(payload, GEMINI_API_KEY)
    structured_data = extract_gemini_recommendations(response)

    # Return predictions and response from Gemini API
    return y_test, y_pred, mae, feature_importance_df, structured_data


# Function to make the API request using curl
def call_gemini_api(payload,GEMINI_API_KEY):
    curl_command = [
        "curl", 
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        "-H", "Content-Type: application/json", 
        "-X", "POST", 
        "-d", json.dumps(payload)
    ]
    
    response = subprocess.run(curl_command, capture_output=True, text=True)
    return response.stdout

import json

def extract_gemini_recommendations(gemini_response):
    # Parse the raw Gemini response to a Python dictionary
    data = json.loads(gemini_response)
    
    # Initialize a dictionary to hold the structured information
    structured_recommendations = {
        "maintenance_actions": "",
        "antenna_inspection_alignment": "",
        "temperature_management": "",
        "humidity_management": "",
        "spectrum_utilization_management": "",
        "precautions": "",
        "best_practices": "",
        "immediate_fixes": ""
    }
    
    # Check if candidates and content exist in the response
    if "candidates" in data and len(data["candidates"]) > 0:
        content = data["candidates"][0]["content"]
        
        # Check if the content contains the recommendation text
        if "parts" in content and len(content["parts"]) > 0:
            recommendation_text = content["parts"][0]["text"]
            
            # Parse specific sections from the text (e.g., Maintenance Actions, Antenna Inspection)
            # Split the text into sections based on headings

            # Extract Maintenance Actions
            if "**1. Maintenance Actions:**" in recommendation_text:
                maintenance_actions_start = recommendation_text.find("**1. Maintenance Actions:**")
                maintenance_actions_end = recommendation_text.find("**2. Precautions:**")
                structured_recommendations["maintenance_actions"] = recommendation_text[maintenance_actions_start:maintenance_actions_end].strip()
            
            # Extract Antenna Inspection and Alignment
            if "Antenna Inspection and Alignment" in recommendation_text:
                antenna_start = recommendation_text.find("Antenna Inspection and Alignment")
                antenna_end = recommendation_text.find("Cable and Connector Check")
                structured_recommendations["antenna_inspection_alignment"] = recommendation_text[antenna_start:antenna_end].strip()
            
            # Extract Temperature Management
            if "Temperature" in recommendation_text:
                temperature_start = recommendation_text.find("Temperature")
                temperature_end = recommendation_text.find("Humidity")
                structured_recommendations["temperature_management"] = recommendation_text[temperature_start:temperature_end].strip()

            # Extract Humidity Management
            if "Humidity" in recommendation_text:
                humidity_start = recommendation_text.find("Humidity")
                humidity_end = recommendation_text.find("Spectrum Utilization")
                structured_recommendations["humidity_management"] = recommendation_text[humidity_start:humidity_end].strip()

            # Extract Spectrum Utilization Management
            if "Spectrum Utilization" in recommendation_text:
                spectrum_start = recommendation_text.find("Spectrum Utilization")
                spectrum_end = recommendation_text.find("2. Precautions:")
                structured_recommendations["spectrum_utilization_management"] = recommendation_text[spectrum_start:spectrum_end].strip()

            # Extract Precautions
            if "**2. Precautions:**" in recommendation_text:
                precautions_start = recommendation_text.find("**2. Precautions:**")
                precautions_end = recommendation_text.find("**3. Best Practices:**")
                structured_recommendations["precautions"] = recommendation_text[precautions_start:precautions_end].strip()
            
            # Extract Best Practices
            if "**3. Best Practices:**" in recommendation_text:
                best_practices_start = recommendation_text.find("**3. Best Practices:**")
                best_practices_end = recommendation_text.find("**4. Immediate Fixes:**")
                structured_recommendations["best_practices"] = recommendation_text[best_practices_start:best_practices_end].strip()

            # Extract Immediate Fixes
            if "**4. Immediate Fixes:**" in recommendation_text:
                immediate_fixes_start = recommendation_text.find("**4. Immediate Fixes:**")
                structured_recommendations["immediate_fixes"] = recommendation_text[immediate_fixes_start:].strip()

    return structured_recommendations