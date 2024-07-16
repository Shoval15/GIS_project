from flask import Flask, request, jsonify
from flask_cors import CORS
from BE import import_data
from BE import greedy_algorithm_topo
from BE import knapsack_problem
from shapely.geometry import Polygon
from BE import utilities

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
    # polygon = utilities.convert_bounds_to_israel_tm(data)
    buildings_gdf = import_data.import_buildings(polygon)
    renewal_gdf = import_data.import_urban_renewal(polygon)
    building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
    gardens_gdf = import_data.import_gardens(polygon)
    # gardens_gdf = import_data.import_land_designations(polygon)
    walking_paths = import_data.import_walking_paths(polygon)

    allocated_gdf, not_allocated_gdf, merged_allocation, allocation_stats = greedy_algorithm_topo.garden_centric_allocation(building_old_and_new_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status)
    print("Allocated buildings:")
    print(allocated_gdf)
    print("\nNot allocated buildings:")
    print(not_allocated_gdf)
    print(f"Total apartments: {allocation_stats['total_apartments']}")
    print(f"Allocated apartments: {allocation_stats['allocated_apartments']}")
    print(f"Not allocated apartments: {allocation_stats['not_allocated_apartments']}")
    print(f"Allocation percentage: {allocation_stats['allocation_percentage']:.2f}%")
    return jsonify({"status": "success", "received": data, "response": merged_allocation})

if __name__ == '__main__':
    app.run(debug=True)
