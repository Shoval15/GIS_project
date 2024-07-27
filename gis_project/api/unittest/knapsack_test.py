import unittest
import geopandas as gpd
from shapely.geometry import Point
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Services import knapsack_problem

class TestKnapsackProblem(unittest.TestCase):
    def setUp(self):
        self.buildings_gdf = gpd.GeoDataFrame({
            'OBJECTID': [1, 2, 3],
            'units_e': [5, 7, 3],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
        })
        self.gardens_gdf = gpd.GeoDataFrame({
            'OBJECTID': [1, 2],
            'capacity': [10, 8],
            'geometry': [Point(0.5, 0.5), Point(1.5, 1.5)]
        })

    def test_garden_centric_allocation(self):
        merged_data, not_allocated, stats, updated_gardens = knapsack_problem.garden_centric_allocation(
            self.buildings_gdf, self.gardens_gdf, None, 1000, 'existing', None, 3, 3.5
        )
        self.assertIsNotNone(merged_data)
        self.assertIsNotNone(not_allocated)
        self.assertIsNotNone(stats)
        self.assertIsNotNone(updated_gardens)
        self.assertEqual(stats['total_apartments'], 15)
        self.assertGreaterEqual(stats['allocated_apartments'], 0)
        self.assertLess(stats['allocated_apartments'], 16)

if __name__ == '__main__':
    unittest.main()