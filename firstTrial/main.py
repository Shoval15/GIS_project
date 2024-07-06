import geopandas as gpd
from scipy.spatial.distance import cdist
from geopy.distance import geodesic
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import shapely.wkt
from pyproj import Proj, transform
import numpy as np
import pyproj
from shapely.geometry import Point, Polygon
from shapely.geometry.base import BaseGeometry
import json

# Define the transformer from Israel TM to WGS84 (latitude and longitude)
transformer = pyproj.Transformer.from_proj(
    pyproj.Proj('epsg:2039'),  # Israel Transverse Mercator
    pyproj.Proj('epsg:4326'))   # WGS84 (latitude and longitude)

# Function to convert a Point or Polygon to WGS84
def convert_to_wgs84(geometry):
    if isinstance(geometry, Point):
        lon, lat = transformer.transform(geometry.x, geometry.y)
        return Point(lon, lat)
    elif isinstance(geometry, Polygon):
        exterior_ring = []
        for x, y in geometry.exterior.coords:
            lon, lat = transformer.transform(x, y)
            exterior_ring.append((lon, lat))
        return Polygon(exterior_ring)
    
# Function to convert a string "(x, y)" to a Point object
def str_to_point(s):
    x, y = map(float, s.strip("()").split(","))
    return Point(x, y)

def calculate_distance(building, garden):
    if not isinstance(building, BaseGeometry) or not isinstance(garden, BaseGeometry):
        return None  # Skip calculation for invalid geometries
    building_coords = (building.centroid.y, building.centroid.x)  
    garden_coords = garden.centroid.y, garden.centroid.x
    return geodesic(building_coords, garden_coords).meters

def read_buildings_file(json_data_path):
    with open(json_data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    features = data['features']
    attributes = [feature['attributes'] for feature in features]
    geometries = [feature['geometry']['rings'][0] for feature in features]
    # Convert geometries to shapely polygons
    polygons = [Polygon(geometry) for geometry in geometries]
    # Create a DataFrame from attributes
    df = pd.DataFrame(attributes)
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=polygons)
    # Set the coordinate reference system (CRS)
    gdf.set_crs(epsg=data['spatialReference']['wkid'], inplace=True)
    return gdf

# Load a shapefile
land_designations_path = 'land_designations/GPL0.shp'  
data = gpd.read_file(land_designations_path)
gardens_data = data[data['MAVAT_NAME'] == 'שטח ציבורי פתוח']
gardens_gdf = gpd.GeoDataFrame(gardens_data, geometry='geometry')

# Load each JSON to a GeoDataFrame
gdf1 = read_buildings_file('north_yovel.json')
gdf2 = read_buildings_file('sourth_yovel.json')
buildings_gdf = pd.concat([gdf1, gdf2], ignore_index=True)

# Apply the conversion function to all geometries in the GeoDataFrames
buildings_gdf['geometry'] = buildings_gdf['geometry'].apply(convert_to_wgs84)
gardens_gdf['geometry'] = gardens_gdf['geometry'].apply(convert_to_wgs84)

# Create an empty DataFrame to store distances
distances_df = pd.DataFrame(columns=['building_id', 'garden_id', 'distance_m'])

# Iterate over buildings and gardens
for building_id, building in buildings_gdf.iterrows():
    for garden_id, garden in gardens_gdf.iterrows():
        distance = calculate_distance(building.geometry, garden.geometry)
        distances_df = distances_df._append({'building_id': building['OBJECTID'], 'garden_id': int(garden_id), 'distance_m': distance}, ignore_index=True)

    distances_df.to_csv('res__.csv', encoding='utf-8')
print(buildings_gdf.columns)

###############################################
# 7 דקות הליכה שוות לכ-0.93 קילומטר.
# Load the CSV data
distances_df = pd.read_csv('res__.csv')
# Merge the CSV data with the GeoDataFrame to get the garden area values
merged_data = distances_df.merge(gardens_gdf[['Shape_STAr']], left_on='garden_id', right_index=True, how='left')
# Merge the CSV data with the GeoDataFrame to get the population values
print(buildings_gdf[['NUM_APTS_C']])

merged_data = merged_data.merge(buildings_gdf[['NUM_APTS_C','OBJECTID']], left_on='building_id', right_on='OBJECTID', how='left')

# Calculate the population based on the number of apartments
merged_data['population'] = merged_data['NUM_APTS_C'] * 3.5
print(merged_data)
data = merged_data
# Define the required garden area per person
required_area_per_person = 3

# Filter out gardens that are more than 1000 meters away from buildings
filtered_data = data[data['distance_m'] <= 1000]

# Initialize a list to store the allocation results
allocation_results = []

# Iterate over each building to allocate gardens
for building_id, group in filtered_data.groupby('building_id'):
    building_people_amount = group['population'].iloc[0]
    required_garden_area = building_people_amount * required_area_per_person
    total_allocated_area = 0
    allocated_gardens = []
    
    # Sort gardens by distance (closest first)
    sorted_gardens = group.sort_values(by='distance_m')
    
    for _, row in sorted_gardens.iterrows():
        garden_id = row['garden_id']
        garden_area = row['Shape_STAr']
        
        if total_allocated_area + garden_area <= required_garden_area:
            allocated_gardens.append(garden_id)
            total_allocated_area += garden_area
        
        if total_allocated_area >= required_garden_area:
            break
    
    allocation_results.append({
        'building_id': building_id,
        'allocated_gardens': allocated_gardens,
        'total_allocated_area': total_allocated_area,
        'required_garden_area': required_garden_area,
        'sufficient_area': total_allocated_area >= required_garden_area
    })

# Convert the allocation results to a DataFrame
allocation_df = pd.DataFrame(allocation_results)

# Display the allocation results
print(allocation_df)

# Save the allocation results to a CSV file
allocation_df.to_csv('garden_allocation_results.csv', index=False)
