from flask import Flask, request, jsonify
from flask_cors import CORS
from Services import import_data
from Services import greedy_algorithm_topo
from Services import knapsack_problem
from shapely.geometry import Polygon
from Services import utilities
import geopandas as gpd
import json
import time

DEBUGGING = False
IMPORT_CACHE = False

app = Flask(__name__)
CORS(app) 

@app.route('/api/bounds', methods=['POST'])
def get_bounds():
    data = request.json
    data_polygon = data['polygon']
    bounds = data['bounds']
    project_status = data['projectStatus']
    apartment_type = data['apartmentType']
    distance = float(data['distance'])*1000
    meters_for_resident = float(data['sqMeterPerResident'])
    residents = float(data['residentsPerApartment'])
    # Create a Polygon from the latlong
    polygon = Polygon(data_polygon)
    if  not utilities.check_polygon_size(polygon):
        return jsonify({"status": "failed", "received": data, "response": "smallPolygon"})
        
    # Extract coordinates
    ne = bounds['northEast']
    sw = bounds['southWest']

    bounds_polygon = Polygon([(sw['lng'], sw['lat']), (ne['lng'], sw['lat']),
                    (ne['lng'], ne['lat']), (sw['lng'], ne['lat'])])


    if DEBUGGING:
        with open('allocated_buildings_with_gardens.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        merged_allocation = gpd.GeoDataFrame.from_features(data)
        with open('not_allocated_buildings.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        not_allocated_gdf = gpd.GeoDataFrame.from_features(data)
        # Assuming the CRS is WGS84 (EPSG:4326)
        merged_allocation.crs = "EPSG:4326"
        allocated_layer = utilities.create_allocated_layer(merged_allocation)
        not_allocated_layer = utilities.create_not_allocated_layer(not_allocated_gdf)        # Calculate allocation statistics
        allocated_apartments = len(merged_allocation)
        not_allocated_apartments = len(not_allocated_gdf)
        total = len(merged_allocation) + len(not_allocated_gdf)
        allocation_stats = {
            "total_apartments": total,
            "allocated_apartments": allocated_apartments,
            "not_allocated_apartments": not_allocated_apartments,
            "allocation_percentage": (allocated_apartments / total) * 100 if total > 0 else 0
        }
        with open('gardens_after_allocation.json', 'r', encoding='utf-8') as file:
            gardens_layer = json.load(file)

        def swap_coordinates(geojson):
            if isinstance(geojson, dict):
                if geojson.get('type') == 'FeatureCollection':
                    for feature in geojson.get('features', []):
                        swap_coordinates(feature)
                elif geojson.get('type') == 'Feature':
                    swap_coordinates(geojson.get('geometry', {}))
                elif geojson.get('type') == 'Polygon':
                    geojson['coordinates'] = [
                        [coord[::-1] for coord in ring]
                        for ring in geojson.get('coordinates', [])
                    ]
            return geojson
        gardens_layer = swap_coordinates(gardens_layer)
        return jsonify({"status": "success",
                        "received": data,
                        "response": {
                            'allocated_layer': allocated_layer,
                            'not_allocated_layer':None,
                            'allocation_stats': allocation_stats,
                            'gardens_layer': gardens_layer
                        }})
    if IMPORT_CACHE:   
        buildings_gdf = gpd.read_file("buildings.geojson")
        renewal_gdf = gpd.read_file("renewal.geojson")
        gardens_gdf = gpd.read_file("gardens.geojson")
    else:
        buildings_gdf = import_data.import_buildings(bounds_polygon, polygon)        
        
        if buildings_gdf.empty:
            return jsonify({"status": "failed", "received": data, "response": "importLayer"})
        
        gardens_gdf = import_data.import_gardens(bounds_polygon, polygon)

        if gardens_gdf.empty :
            return jsonify({"status": "failed", "received": data, "response": "importLayer"})
            
        renewal_gdf = import_data.import_urban_renewal(bounds_polygon, polygon)
        
    building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
    walking_paths = import_data.import_walking_paths(polygon)
    if walking_paths is None:
        return jsonify({"status": "failed", "received": data, "response": "importLayer"})

    # merged_allocation, not_allocated_gdf, allocation_stats, gardens_gdf = greedy_algorithm_topo.garden_centric_allocation(
    #     building_old_and_new_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status, meters_for_resident, residents)
    merged_allocation, not_allocated_gdf, allocation_stats, gardens_gdf = knapsack_problem.garden_centric_allocation(
        building_old_and_new_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status, meters_for_resident, residents)
    allocated_layer = utilities.create_allocated_layer(merged_allocation)
    not_allocated_layer = utilities.create_not_allocated_layer(not_allocated_gdf)
    gardens_layer = utilities.create_gardens_layer(gardens_gdf)
    return jsonify({"status": "success",
                    "received": data,
                    "response": {
                        'allocated_layer': allocated_layer,
                        'not_allocated_layer':not_allocated_layer,
                        'allocation_stats': allocation_stats,
                        'gardens_layer': gardens_layer
                    }})

if __name__ == '__main__':
    app.run(debug=True)
