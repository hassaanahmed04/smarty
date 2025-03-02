# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from flask import Flask, render_template, jsonify
import csv
from .helperfunction import load_data, predict_interference, predict_failure_rate
import numpy as np 

@blueprint.route('/api/interference', methods=['GET'])
def get_interference():
    # Load your data
    df = load_data()  # Your code to load the data
    
    # Get predictions for interference
    interference_predictions = predict_interference(df)  # Your prediction function
    
    # Since `interference_predictions` is already a dictionary of lists, no need to call `.tolist()` here.
    return jsonify(interference_predictions)

from flask import request, jsonify
@blueprint.route('/api/failure_rate', methods=['GET'])
def get_failure_rate():
    # Get cluster name from the request
    cluster_name = request.args.get('cluster_name', default=None, type=str)
    
    if cluster_name is None:
        return jsonify({'error': 'Cluster name is required'}), 400
    
    # Load the data
    df = load_data()
    # Filter data based on the cluster_name
    df_filtered = df[df['Cluster'] == cluster_name]
    
    if df_filtered.empty:
        return jsonify({'error': f'No data found for cluster: {cluster_name}'}), 404

    # Predict failure rate using the filtered data
    y_test, y_pred, mae, feature_importance_df, response = predict_failure_rate(df_filtered, cluster_name)
    
    # Ensure y_pred is a NumPy array before calling .tolist()
    if isinstance(y_pred, np.ndarray):
        y_pred_list = y_pred.tolist()
    else:
        # In case y_pred is a float, we can wrap it in a list
        y_pred_list = [y_pred]

    # Convert DataFrame to dictionary for JSON serialization
    feature_importance_dict = feature_importance_df.to_dict(orient='records')

    # Prepare the response data
    return jsonify({
        'mae': mae,
        'failure_rate_predictions': y_pred_list,
        'actual_failure_rate': y_test.tolist(),
        'feature_importance': feature_importance_dict,
        'response_ai': response 
    })





def read_tv_spectrum():
    data = []
    with open("dataset/tv_spectrum_lesotho.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["latitude"] = float(row["latitude"])
            row["longitude"] = float(row["longitude"])
            row["available_channels"] = eval(row["available_channels"])
            row["occupied_channels"] = eval(row["occupied_channels"])
            row["signal_strength"] = float(row["signal_strength"])
            row["interference_level"] = row["interference_level"]
            data.append(row)
    return data

def read_schools():
    schools = []
    with open("dataset/affected_schools_only.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["latitude"] = float(row["Latitude"])
            row["longitude"] = float(row["Longitude"])
            row["name"] = row["School Name"]
            schools.append(row)
    return schools
def read_all_schools():
    schools = []
    with open("dataset/school_data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["latitude"] = float(row["Latitude"])
            row["longitude"] = float(row["Longitude"])
            row["name"] = row["School Name"]
            schools.append(row)
    return schools
def read_towers():
    towers = []
    with open("dataset/lesotho.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["latitude"] = float(row["lat"])
            row["longitude"] = float(row["lon"])
            row["type"] = row["radio"]
            towers.append(row)
    return towers

import json

def read_geojson():
    # Initialize an empty list to hold the processed data
    data = []
    
    # Open the GeoJSON file and load its content
    with open("dataset/tvws_stations.geojson", "r") as file:
        geojson_data = json.load(file)
        
        # Iterate over the features in the GeoJSON
        for feature in geojson_data["features"]:
            # Extract the properties and geometry from each feature
            properties = feature["properties"]
            geometry = feature["geometry"]
            
            # Extract the coordinates from the geometry
            longitude, latitude,= geometry["coordinates"]
            
            # Prepare the row with necessary fields
            row = {
                "cluster": properties["Cluster"],
                "available_channels": properties["Available Channels"],
                "interference": properties["Interference"],
                "elevation": properties["Elevation"],
                "population": properties["Population"],
                "density": properties["Density"],
                "tvws_range_km": properties["TVWS Range (km)"],
                "affected_schools":properties["Affected Schools"],
                "latitude": latitude,
                "longitude": longitude
            }
            
            # Append the row to the data list
            data.append(row)
    
    # Return the processed data
    return data

def read_data_by_cluster():
    clusters = {}
    with open("dataset/tvws_historical_data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cluster = row["Cluster"]
            row["date"] = row["date"]
            row["available_channels"] = eval(row["Available Channels"])  # Convert string list to actual list
            row["interference"] = row["Interference"]
            row["elevation"] = float(row["Elevation"])
            row["population"] = int(row["Population"])
            row["density"] = float(row["Density"])
            row["tvws_range_km"] = float(row["TVWS Range (km)"])
            row["signal_strength_dbm"] = float(row["Signal Strength (dBm)"])
            row["spectrum_utilization"] = float(row["Spectrum Utilization (%)"])
            row["temperature_c"] = float(row["Temperature (°C)"])
            row["humidity"] = float(row["Humidity (%)"])
            row["interference_level"] = row["Interference Level"]
            row["failure_rate"] = float(row["Failure Rate (%)"])
            
            if cluster not in clusters:
                clusters[cluster] = []
            clusters[cluster].append(row)
    return clusters

@blueprint.route("/clusters")
def get_clusters():
    cluster_name = request.args.get("cluster")
    clusters = read_data_by_cluster()
    
    if cluster_name:
        return jsonify({cluster_name: clusters.get(cluster_name, [])})
    
    return jsonify(clusters)

@blueprint.route("/geojson_data")
def get_geojson_data():
    geojson_data = read_geojson()
    return jsonify(geojson_data)

# This is the root route
@blueprint.route('/dashboard')
def index():
    return render_template('home/index.html', segment='index')

# Route for towers data
@blueprint.route("/towers")
def get_towers():
    towers = read_towers()
    return jsonify(towers)

# Route for schools data
@blueprint.route("/schools")
def get_schools():
    schools = read_schools()
    return jsonify(schools)

@blueprint.route("/allschools")
def get_all_schools():
    allschools = read_all_schools()
    return jsonify(allschools)
# Renamed this function to avoid conflict
@blueprint.route("/")
def map_view():
    return render_template("home/landing.html")

# Route for tv spectrum data
@blueprint.route("/data")
def get_data():
    data = read_tv_spectrum()
    return jsonify(data)

# Catch-all route for other templates
@blueprint.route('/<template>')
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None
