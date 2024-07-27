import unittest
from shapely.geometry import Point, Polygon
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Services import utilities
import geopandas as gpd

class TestUtilities(unittest.TestCase):
    def test_convert_coords(self):
        point = Point(35.2, 31.8)
        converted_point = utilities.convert_coords(point)
        self.assertIsInstance(converted_point, Point)
        self.assertNotEqual(point.x, converted_point.x)
        self.assertNotEqual(point.y, converted_point.y)

    def test_calculate_min_distance(self):
        building = Point(0, 0)
        garden = Polygon([(1, 1), (2, 1), (2, 2), (1, 2)])
        distance = utilities.calculate_min_distance(building, garden)
        self.assertGreater(distance, 0)

    def test_remove_empty_buildings(self):
        
        buildings_gdf = gpd.GeoDataFrame({
            'OBJECTID': [1, 2, 3],
            'units_e': [5, 0, 10],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
        })
        filtered_gdf = utilities.remove_empty_buildings(buildings_gdf)
        self.assertEqual(len(filtered_gdf), 2)
        self.assertNotIn(0, filtered_gdf['units_e'].values)

if __name__ == '__main__':
    unittest.main()