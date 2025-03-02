# import random
# import json
# import pandas as pd
# from datetime import datetime, timedelta

# # TVWS Device Details
# tvws_data = {
#     "type": "FeatureCollection",
#     "features": [
#         {
#             "type": "Feature",
#             "properties": {
#                 "Cluster": "Lesotho_tvws_0",
#                 "Available Channels": [41, 25, 30, 66, 58],
#                 "Interference": "Low",
#                 "Elevation": 881.0,
#                 "Population": 39085,
#                 "Density": 26.83,
#                 "TVWS Range (km)": 30
#             },
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [27.512340996047893, -29.65557971538073]
#             }
#         },
#         {
#             "type": "Feature",
#             "properties": {
#                 "Cluster": "Lesotho_tvws_1",
#                 "Available Channels": [54, 25, 41, 30, 66],
#                 "Interference": "Low",
#                 "Elevation": 264.0,
#                 "Population": 39085,
#                 "Density": 26.83,
#                 "TVWS Range (km)": 30
#             },
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [28.668014521889845, -29.537868284843338]
#             }
#         },
#         {
#             "type": "Feature",
#             "properties": {
#                 "Cluster": "Lesotho_tvws_2",
#                 "Available Channels": [45, 58, 30, 66, 41],
#                 "Interference": "Low",
#                 "Elevation": 1914.0,
#                 "Population": 39085,
#                 "Density": 26.83,
#                 "TVWS Range (km)": 30
#             },
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [28.020362836923173, -28.989643973734843]
#             }
#         },
#         {
#             "type": "Feature",
#             "properties": {
#                 "Cluster": "Lesotho_tvws_3",
#                 "Available Channels": [45, 58, 50, 22, 66, 30],
#                 "Interference": "Low",
#                 "Elevation": 1021.0,
#                 "Population": 39085,
#                 "Density": 26.83,
#                 "TVWS Range (km)": 30
#             },
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [27.989827226337635, -30.179441298099988]
#             }
#         }
#     ]
# }

# # Helper function to generate random data
# def generate_historical_data(cluster_data, start_date, end_date):
#     date_range = pd.date_range(start_date, end_date, freq='D')
#     historical_data = []
    
#     for date in date_range:
#         for feature in cluster_data['features']:
#             cluster = feature['properties']['Cluster']
#             available_channels = feature['properties']['Available Channels']
#             interference = feature['properties']['Interference']
#             elevation = feature['properties']['Elevation']
#             population = feature['properties']['Population']
#             density = feature['properties']['Density']
#             tvws_range = feature['properties']['TVWS Range (km)']
            
#             # Randomly simulate data for the day
#             signal_strength = random.uniform(10, 100)  # Signal strength between 10-100
#             spectrum_utilization = random.uniform(0.5, 1.0)  # 50% to 100% utilization
#             temperature = random.uniform(15, 35)  # Random temperature in Celsius
#             humidity = random.uniform(30, 90)  # Random humidity
#             interference_level = random.choice(["Low", "Medium", "High"])  # Random interference
#             failure_rate = random.uniform(0, 0.05)  # Failure rate in percentage (0 to 5%)
            
#             data_entry = {
#                 "date": date,
#                 "Cluster": cluster,
#                 "Available Channels": available_channels,
#                 "Interference": interference,
#                 "Elevation": elevation,
#                 "Population": population,
#                 "Density": density,
#                 "TVWS Range (km)": tvws_range,
#                 "Signal Strength (dBm)": signal_strength,
#                 "Spectrum Utilization (%)": spectrum_utilization * 100,
#                 "Temperature (°C)": temperature,
#                 "Humidity (%)": humidity,
#                 "Interference Level": interference_level,
#                 "Failure Rate (%)": failure_rate * 100
#             }
            
#             historical_data.append(data_entry)
    
#     return historical_data

# # Generate historical data for a specific time period
# start_date = '2020-01-01'
# end_date = '2024-12-31'

# historical_data = generate_historical_data(tvws_data, start_date, end_date)

# # Convert to DataFrame for better readability or analysis
# df = pd.DataFrame(historical_data)

# # Display first few rows of generated data
# print(df.head())

# # Optionally, save this data to a CSV file for future use
# df.to_csv('tvws_historical_data.csv', index=False)

# import pandas as pd
# import numpy as np
# import Faker
# import random

# # Initialize Faker
# fake = Faker()

# # Generate synthetic vendor data
# def generate_vendors(num_vendors=10):
#     vendors = []
#     for _ in range(num_vendors):
#         vendor = {
#             'vendor_id': fake.uuid4(),
#             'company_name': fake.company(),
#             'country': fake.country(),
#             'base_station_cost': round(np.random.uniform(1000, 10000), 2),
#             'antenna_cost': round(np.random.uniform(500, 2000), 2),
#             'backhaul_cost': round(random.choice([5000, 10000, 15000, 20000]), 2),
#             'installation_cost': round(np.random.lognormal(7, 0.5), 2),
#             'spectrum_license_fee': round(np.random.uniform(0, 5000), 2),  # Some countries have 0 fee
#             'maintenance_cost_per_year': round(np.random.uniform(500, 2000), 2),
#             'coverage_radius_km': random.choice([10, 20, 30, 50, 100]),
#             'power_option': random.choice(['Solar', 'Grid', 'Hybrid']),
#             'warranty_years': random.randint(1, 5),
#             'rating': round(np.random.uniform(3.0, 5.0), 1),
#             'delivery_time_weeks': random.randint(2, 12),
#             'supported_standards': random.sample(['IEEE 802.22', 'IEEE 802.11af', 'Custom'], k=1)[0],
#             'last_updated': fake.date_this_decade()
#         }
#         vendors.append(vendor)
#     return pd.DataFrame(vendors)

# # Generate procurement-specific features
# def add_procurement_features(df):
#     df['total_initial_cost'] = df[[
#         'base_station_cost',
#         'antenna_cost',
#         'backhaul_cost',
#         'installation_cost',
#         'spectrum_license_fee'
#     ]].sum(axis=1)
    
#     df['annual_operational_cost'] = df['maintenance_cost_per_year'] + \
#                                    (df['backhaul_cost'] * 0.1)  # Assuming 10% of backhaul cost as annual fee
    
#     df['cost_per_km2'] = df['total_initial_cost'] / (3.14 * (df['coverage_radius_km']**2))
#     return df

# # Generate dataset
# num_vendors = 50  # Generate 50 vendor entries
# vendor_df = generate_vendors(num_vendors)
# vendor_df = add_procurement_features(vendor_df)

# # Save to CSV
# vendor_df.to_csv('tvws_vendor_dataset.csv', index=False)

# # Display sample
# print(vendor_df[['company_name', 'country', 'total_initial_cost', 
#                'coverage_radius_km', 'rating']].head(5))
import csv
import json
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

def load_geojson_polygon(geojson_path):
    """Loads a polygon from a GeoJSON file."""
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)
        coordinates = geojson['features'][0]['geometry']['coordinates'][0]
        return Polygon(coordinates)

def adjust_coordinates_to_polygon(lat, lon, polygon):
    """Adjusts coordinates to the nearest point inside the polygon if they are outside."""
    point = Point(lon, lat)
    if polygon.contains(point):
        return lat, lon  # Already inside
    
    nearest_point = nearest_points(polygon, point)[0]
    return nearest_point.y, nearest_point.x  # Convert back to (lat, lon)

def update_csv_coordinates(csv_path, output_csv_path, polygon):
    """Updates coordinates in a CSV file to ensure they remain inside the given polygon."""
    with open(csv_path, 'r') as infile, open(output_csv_path, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        header = next(reader)  # Read header
        writer.writerow(header)  # Write header to new CSV
        
        for row in reader:
            latitude, longitude = float(row[0]), float(row[1])
            new_lat, new_lon = adjust_coordinates_to_polygon(latitude, longitude, polygon)
            row[0], row[1] = new_lat, new_lon  # Update with new coordinates
            writer.writerow(row)
if __name__ == "__main__":
    geojson_path = "dataset/ls.json"  # Path to your GeoJSON file
    csv_path = "dataset/tv_spectrum_lesotho copy.csv"  # Path to your input CSV file
    output_csv_path = "filtered_output.csv"  # Path to save the filtered CSV
    
    polygon = load_geojson_polygon(geojson_path)
    update_csv_coordinates(csv_path, output_csv_path, polygon)
    print("Filtered CSV has been saved.")