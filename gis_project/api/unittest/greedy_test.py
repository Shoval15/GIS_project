import unittest
import geopandas as gpd
from shapely.geometry import Point, Polygon
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Services import greedy_algorithm_topo
from Services import utilities

class TestGreedyAlgorithm(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.buildings_gdf = gpd.GeoDataFrame({
            'OBJECTID': [1, 2, 3, 4],
            'units_e': [10, 15, 20, 5],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)],
            'gen_status': ['exists', 'exists', 'renewal', 'exists'],
            'address': ['Address 1', 'Address 2', 'Address 3', 'Address 4']
        })
        
        self.gardens_gdf = gpd.GeoDataFrame({
            'OBJECTID': [1, 2],
            'Shape.STArea()': [1000, 1500],
            'YEUD': [670, 670],
            'Descr': ['Garden 1', 'Garden 2'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), 
                         Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])]
        })
        
        # Mock walking paths (normally this would be a graph)
        self.walking_paths = None

    def test_garden_centric_allocation(self):
        distance = 1000  # 1 km
        apartment_type = 'existing'
        project_status = None
        meters_for_resident = 3
        residents = 3.5

        merged_data, not_allocated_buildings, allocation_stats, updated_gardens = greedy_algorithm_topo.garden_centric_allocation(
            self.buildings_gdf, self.gardens_gdf, self.walking_paths, distance, 
            apartment_type, project_status, meters_for_resident, residents
        )

        # Check that the function returns the expected types
        self.assertIsInstance(merged_data, gpd.GeoDataFrame)
        self.assertIsInstance(not_allocated_buildings, gpd.GeoDataFrame)
        self.assertIsInstance(allocation_stats, dict)
        self.assertIsInstance(updated_gardens, gpd.GeoDataFrame)

        # Check that all buildings are accounted for
        total_buildings = len(merged_data) + len(not_allocated_buildings)
        self.assertEqual(total_buildings, len(self.buildings_gdf))

        # Check allocation stats
        self.assertEqual(allocation_stats['total_apartments'], self.buildings_gdf['units_e'].sum())
        self.assertGreaterEqual(allocation_stats['allocated_apartments'], 0)
        self.assertLessEqual(allocation_stats['allocated_apartments'], allocation_stats['total_apartments'])

        # Check that allocated buildings have garden information
        if not merged_data.empty:
            self.assertIn('allocated_garden', merged_data.columns)
            self.assertIn('OBJECTID_garden', merged_data.columns)

        # Check that garden capacities have been updated
        self.assertIn('remaining_capacity', updated_gardens.columns)
        self.assertTrue(all(updated_gardens['remaining_capacity'] >= 0))

    def test_empty_input(self):
        empty_buildings = gpd.GeoDataFrame()
        empty_gardens = gpd.GeoDataFrame()

        merged_data, not_allocated_buildings, allocation_stats, updated_gardens = greedy_algorithm_topo.garden_centric_allocation(
            empty_buildings, empty_gardens, self.walking_paths, 1000, 'existing', None, 3, 3.5
        )

        self.assertTrue(merged_data.empty)
        self.assertTrue(not_allocated_buildings.empty)
        self.assertEqual(allocation_stats['total_apartments'], 0)
        self.assertEqual(allocation_stats['allocated_apartments'], 0)

if __name__ == '__main__':
    unittest.main()