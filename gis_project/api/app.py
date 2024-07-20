from flask import Flask, request, jsonify
from flask_cors import CORS
from BE import import_data
from BE import greedy_algorithm_topo
from BE import knapsack_problem
from shapely.geometry import Polygon
from BE import utilities
import geopandas as gpd
import json
from firebase_functions import https_fn
import time

app = Flask(__name__)
CORS(app) 

@app.route('/api/bounds', methods=['POST'])
def get_bounds():
    data = request.json
    bounds = data['bounds']
    project_status = data['projectStatus']
    apartment_type = data['apartmentType']
    distance = float(data['distance'])*1000
    
    # Extract coordinates
    ne = bounds['northEast']
    sw = bounds['southWest']
    
    # Create a Polygon from the bounds
    polygon = Polygon([(sw['lng'], sw['lat']), (ne['lng'], sw['lat']),
                       (ne['lng'], ne['lat']), (sw['lng'], ne['lat'])])

    if  not utilities.check_polygon_size(polygon):
        return jsonify({"status": "failed", "received": data, "response": "smallPolygon"})
    
    """
    buildings_gdf = import_data.import_buildings(polygon)
    if buildings_gdf.empty:
        return jsonify({"status": "failed", "received": data, "response": "importLayer"})
    renewal_gdf = import_data.import_urban_renewal(polygon)
    if renewal_gdf.empty :
        if apartment_type == 'proposed':
            return jsonify({"status": "failed", "received": data, "response": "importLayer"})
        else:
            building_old_and_new_gdf = buildings_gdf
            building_old_and_new_gdf['gen_status'] = 'exists'
    else:        
        building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
    gardens_gdf = import_data.import_gardens(polygon)
    if gardens_gdf.empty :
        return jsonify({"status": "failed", "received": data, "response": "importLayer"})
    walking_paths = import_data.import_walking_paths(polygon)
    if walking_paths is None:
        return jsonify({"status": "failed", "received": data, "response": "importLayer"})

    allocated_gdf, not_allocated_gdf, merged_allocation, allocation_stats, gardens_gdf = greedy_algorithm_topo.garden_centric_allocation(building_old_and_new_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status)
    allocated_layer = utilities.create_allocated_layer(merged_allocation)
    not_allocated_layer = utilities.create_not_allocated_layer(not_allocated_gdf)
    gardens_layer = utilities.create_gardens_layer(gardens_gdf)

    print("Allocated buildings:")
    print(allocated_gdf)
    print("\nNot allocated buildings:")
    print(not_allocated_gdf)
    print(f"Total apartments: {allocation_stats['total_apartments']}")
    print(f"Allocated apartments: {allocation_stats['allocated_apartments']}")
    print(f"Not allocated apartments: {allocation_stats['not_allocated_apartments']}")
    print(f"Allocation percentage: {allocation_stats['allocation_percentage']:.2f}%")
    """

    # For debugging:
    with open('allocated_buildings_with_gardens.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    print(data['features'][:10])
    merged_allocation = gpd.GeoDataFrame.from_features(data)
    print(merged_allocation)
    # Assuming the CRS is WGS84 (EPSG:4326)
    merged_allocation.crs = "EPSG:4326"
    allocated_layer = utilities.create_allocated_layer(merged_allocation)
    not_allocated_layer = allocated_layer
    # Calculate allocation statistics
    allocated_apartments = len(merged_allocation)
    not_allocated_apartments = 900 - allocated_apartments
    allocation_stats = {
        "total_apartments": 900,
        "allocated_apartments": allocated_apartments,
        "not_allocated_apartments": not_allocated_apartments,
        "allocation_percentage": (allocated_apartments / 900) * 100 if 900 > 0 else 0
    }
    gardens_layer = allocated_layer
    # End debugging
    time.sleep(5)
    return jsonify({"status": "success",
                    "received": data,
                    "response": {
                        'allocated_layer': allocated_layer,
                        'not_allocated_layer':not_allocated_layer,
                        'allocation_stats': allocation_stats,
                        'gardens_layer': gardens_layer
                    }})

# @https_fn.on_request()
# def serve_flask_app(request):
#     with app.test_request_context():
#         return app.full_dispatch_request()
    
if __name__ == '__main__':
    app.run(debug=True)
