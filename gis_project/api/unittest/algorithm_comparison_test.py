import unittest
import time
import geopandas as gpd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Services import greedy_algorithm_topo
from Services import knapsack_problem
from Services import utilities
from Services import import_data
import os
from shapely.geometry import box, Polygon
import osmnx as ox
import networkx as nx

class TestAlgorithmComparison(unittest.TestCase):
    def setUp(self):
        # Load cached GeoJSON files
        cache_dir = '../services/myCache/data'
        self.buildings_gdf = gpd.read_file(os.path.join(cache_dir, 'buildings.geojson'))
        self.gardens_gdf = gpd.read_file(os.path.join(cache_dir, 'gardens.geojson'))
        self.renewal_gdf = gpd.read_file(os.path.join(cache_dir, 'renewal.geojson'))

        # Combine buildings and renewal data
        self.buildings_gdf = import_data.union_building_and_renewal(self.buildings_gdf, self.renewal_gdf)

        # Get the bounds of the area
        minx, miny, maxx, maxy = self.buildings_gdf.total_bounds
        self.bounds = box(minx, miny, maxx, maxy)
        self.bounds_polygon = Polygon([(miny, minx), (miny, maxx), (maxy, maxx), (maxy, minx)])

        print(f"Area bounds: {self.bounds}")

        # Get the walking paths graph
        self.walking_paths = import_data.import_walking_paths(self.bounds_polygon)

        print(f"Walking paths graph: {len(self.walking_paths.nodes)} nodes, {len(self.walking_paths.edges)} edges")

    def run_algorithm(self, algorithm, name):
        start_time = time.time()
        merged_data, not_allocated_buildings, allocation_stats, updated_gardens = algorithm(
            self.buildings_gdf, self.gardens_gdf, self.walking_paths, 1000, 'existing', None, 3, 3.5
        )
        end_time = time.time()

        execution_time = end_time - start_time
        allocated_percentage = allocation_stats['allocation_percentage']
        
        print(f"\n{name} Algorithm Results:")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Allocated Percentage: {allocated_percentage:.2f}%")
        print(f"Total Apartments: {allocation_stats['total_apartments']}")
        print(f"Allocated Apartments: {allocation_stats['allocated_apartments']}")
        print(f"Not Allocated Apartments: {allocation_stats['not_allocated_apartments']}")

        return execution_time, allocated_percentage, allocation_stats

    def test_algorithm_comparison(self):
        print("\nComparing Greedy and Knapsack Algorithms:")
        
        greedy_time, greedy_percentage, greedy_stats = self.run_algorithm(
            greedy_algorithm_topo.garden_centric_allocation, "Greedy"
        )
        
        knapsack_time, knapsack_percentage, knapsack_stats = self.run_algorithm(
            knapsack_problem.garden_centric_allocation, "Knapsack"
        )

        print("\nComparison Summary:")
        print(f"Greedy Algorithm Time: {greedy_time:.2f} seconds")
        print(f"Knapsack Algorithm Time: {knapsack_time:.2f} seconds")
        print(f"Time Difference: {abs(greedy_time - knapsack_time):.2f} seconds")
        print(f"Greedy Allocation Percentage: {greedy_percentage:.2f}%")
        print(f"Knapsack Allocation Percentage: {knapsack_percentage:.2f}%")
        print(f"Allocation Difference: {abs(greedy_percentage - knapsack_percentage):.2f}%")

        # Assert that both algorithms allocate some apartments
        self.assertGreater(greedy_stats['allocated_apartments'], 0)
        self.assertGreater(knapsack_stats['allocated_apartments'], 0)

        # Check if one algorithm significantly outperforms the other
        if abs(greedy_percentage - knapsack_percentage) > 10:
            better_algorithm = "Knapsack" if knapsack_percentage > greedy_percentage else "Greedy"
            print(f"\nNote: {better_algorithm} algorithm performed significantly better in terms of allocation percentage.")

        if abs(greedy_time - knapsack_time) > 5:
            faster_algorithm = "Knapsack" if knapsack_time < greedy_time else "Greedy"
            print(f"\nNote: {faster_algorithm} algorithm was significantly faster.")

if __name__ == '__main__':
    unittest.main()