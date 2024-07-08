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
    # Extract coordinates
    ne = data['northEast']
    sw = data['southWest']
    
    # Create a Polygon from the bounds
    polygon = Polygon([(sw['lng'], sw['lat']), (ne['lng'], sw['lat']),
                       (ne['lng'], ne['lat']), (sw['lng'], ne['lat'])])
    # polygon = utilities.convert_bounds_to_israel_tm(data)
    print(polygon)
    buildings_gdf = import_data.import_buildings(polygon)
    gardens_gdf = import_data.import_land_designations(polygon)
    walking_paths = import_data.import_walking_paths(polygon)
    print("Received bounds:", data)
    print(buildings_gdf)
    print(gardens_gdf)
    print(walking_paths)
    return jsonify({"status": "success", "received": data})

if __name__ == '__main__':
    app.run(debug=True)
