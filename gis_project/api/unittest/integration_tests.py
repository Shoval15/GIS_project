import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from shapely.geometry import Polygon, Point
from geopandas import GeoDataFrame
import networkx as nx
from flask import Flask
from Services import import_data, utilities, distance_walk, knapsack_problem
from app import app
from shapely import wkt

class UrbanGreenSpaceAnalyzerIntegrationTests(unittest.TestCase):

    def setUp(self):
        # Set up test data
        self.test_bounds = wkt.loads("POLYGON ((35.175733064358006 31.75145736055472, 35.18031023041166 31.75145736055472, 35.18031023041166 31.756657407735275, 35.175733064358006 31.756657407735275, 35.175733064358006 31.75145736055472))")
        self.test_polygon = wkt.loads("POLYGON ((35.175733064358006 31.75663916246635, 35.17629177946315 31.75145736055472, 35.18031023041166 31.7527163461439, 35.179815982434036 31.756657407735275, 35.177344742545905 31.756073557345953, 35.175733064358006 31.75663916246635))")
        self.apartment_type = "proposed"
        self.project_status = "תכנית מאושרת"
        self.distance = 960
        self.meters_for_resident = 3
        self.residents = 3.5

    def test_data_import_and_preprocessing(self):
        # Import data
        buildings_gdf = import_data.import_buildings(self.test_bounds, self.test_polygon)
        gardens_gdf = import_data.import_gardens(self.test_bounds, self.test_polygon)
        renewal_gdf = import_data.import_urban_renewal(self.test_bounds, self.test_polygon)
        building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
        walking_paths = import_data.import_walking_paths(self.test_polygon)

        # Preprocess data
        buildings_gdf, gardens_gdf = utilities.preprocess_data(
            building_old_and_new_gdf, gardens_gdf, walking_paths, 
            self.apartment_type, self.project_status, self.distance, 
            self.meters_for_resident, self.residents
        )

        # Assertions
        self.assertFalse(buildings_gdf.empty, "Buildings GeoDataFrame should not be empty")
        self.assertFalse(gardens_gdf.empty, "Gardens GeoDataFrame should not be empty")
        self.assertIn('nearby_buildings', gardens_gdf.columns, "Gardens should have 'nearby_buildings' column after preprocessing")
        self.assertIn('capacity', gardens_gdf.columns, "Gardens should have 'capacity' column after preprocessing")

    def test_allocation_algorithm(self):
        # Use the same setup as in the previous test
        buildings_gdf = import_data.import_buildings(self.test_bounds, self.test_polygon)
        gardens_gdf = import_data.import_gardens(self.test_bounds, self.test_polygon)
        renewal_gdf = import_data.import_urban_renewal(self.test_bounds, self.test_polygon)
        building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
        walking_paths = import_data.import_walking_paths(self.test_polygon)

        buildings_gdf, gardens_gdf = utilities.preprocess_data(
            building_old_and_new_gdf, gardens_gdf, walking_paths, 
            self.apartment_type, self.project_status, self.distance, 
            self.meters_for_resident, self.residents
        )

        # Run allocation algorithm
        merged_data, not_allocated_buildings, allocation_stats, updated_gardens_gdf = knapsack_problem.garden_centric_allocation(
            buildings_gdf, gardens_gdf, walking_paths, self.distance, 
            self.apartment_type, self.project_status, self.meters_for_resident, self.residents
        )

        # Assertions
        self.assertFalse(merged_data.empty, "Merged data should not be empty")
        self.assertIn('allocated_garden', merged_data.columns, "Merged data should have 'allocated_garden' column")
        self.assertGreater(allocation_stats['total_apartments'], 0, "There should be apartments to allocate")
        self.assertGreater(allocation_stats['allocated_apartments'], 0, "Some apartments should be allocated")
        self.assertGreater(allocation_stats['allocation_percentage'], 0, "Allocation percentage should be greater than 0")

    def test_distance_calculation(self):
        # Create a simple test graph
        G = nx.Graph()
        G.add_edge(1, 2, length=100, time=1)
        G.add_edge(2, 3, length=200, time=2)

        # Define test points
        point1 = Point(0, 0)
        point2 = Point(3, 0)

        # Calculate distance
        distance = distance_walk.calculate_walk_distance(G, point1, point2)

        # Assertion
        self.assertEqual(distance, 300, f"Expected distance of 300, but got {distance}")

    def test_geojson_creation(self):
        # Use the same setup and allocation as in the previous tests
        buildings_gdf = import_data.import_buildings(self.test_bounds, self.test_polygon)
        gardens_gdf = import_data.import_gardens(self.test_bounds, self.test_polygon)
        renewal_gdf = import_data.import_urban_renewal(self.test_bounds, self.test_polygon)
        building_old_and_new_gdf = import_data.union_building_and_renewal(buildings_gdf, renewal_gdf)
        walking_paths = import_data.import_walking_paths(self.test_polygon)

        buildings_gdf, gardens_gdf = utilities.preprocess_data(
            building_old_and_new_gdf, gardens_gdf, walking_paths, 
            self.apartment_type, self.project_status, self.distance, 
            self.meters_for_resident, self.residents
        )

        merged_data, not_allocated_buildings, allocation_stats, updated_gardens_gdf = knapsack_problem.garden_centric_allocation(
            buildings_gdf, gardens_gdf, walking_paths, self.distance, 
            self.apartment_type, self.project_status, self.meters_for_resident, self.residents
        )

        # Create GeoJSON layers
        allocated_layer = utilities.create_allocated_layer(merged_data)
        not_allocated_layer = utilities.create_not_allocated_layer(not_allocated_buildings)
        gardens_layer = utilities.create_gardens_layer(updated_gardens_gdf)

        # Assertions
        self.assertGreater(len(allocated_layer['features']), 0, "Allocated layer should have features")
        self.assertGreater(len(not_allocated_layer['features']), 0, "Not allocated layer should have features")
        self.assertGreater(len(gardens_layer['features']), 0, "Gardens layer should have features")

    def test_api_endpoint(self):
        client = app.test_client()

        # Prepare test data
        test_data = {
            "polygon": self.test_polygon.__geo_interface__,
            "bounds": self.test_bounds.__geo_interface__,
            "projectStatus": self.project_status,
            "apartmentType": self.apartment_type,
            "distance": str(self.distance / 1000),  # Convert to km
            "sqMeterPerResident": str(self.meters_for_resident),
            "residentsPerApartment": str(self.residents)
        }

        # Make a POST request to the API
        response = client.post('/api/bounds', json=test_data)

        # Assertions
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        data = response.get_json()
        self.assertEqual(data['status'], 'success', f"Expected status 'success', but got {data['status']}")
        self.assertIn('allocated_layer', data['response'], "Response should include allocated_layer")
        self.assertIn('not_allocated_layer', data['response'], "Response should include not_allocated_layer")
        self.assertIn('allocation_stats', data['response'], "Response should include allocation_stats")
        self.assertIn('gardens_layer', data['response'], "Response should include gardens_layer")

if __name__ == '__main__':
    unittest.main()