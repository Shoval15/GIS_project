import unittest
from shapely.geometry import Polygon
from Services import import_data

class TestImportData(unittest.TestCase):
    def setUp(self):
        self.test_bounds = Polygon([(35.1, 31.7), (35.2, 31.7), (35.2, 31.8), (35.1, 31.8)])

    def test_import_buildings(self):
        buildings_gdf = import_data.import_buildings(self.test_bounds, self.test_bounds)
        self.assertIsNotNone(buildings_gdf)
        self.assertFalse(buildings_gdf.empty)
        self.assertIn('OBJECTID', buildings_gdf.columns)
        self.assertIn('geometry', buildings_gdf.columns)

    def test_import_gardens(self):
        gardens_gdf = import_data.import_gardens(self.test_bounds, self.test_bounds)
        self.assertIsNotNone(gardens_gdf)
        self.assertFalse(gardens_gdf.empty)
        self.assertIn('OBJECTID', gardens_gdf.columns)
        self.assertIn('geometry', gardens_gdf.columns)

    def test_import_walking_paths(self):
        walking_paths = import_data.import_walking_paths(self.test_bounds)
        self.assertIsNotNone(walking_paths)
        self.assertTrue(len(walking_paths.nodes) > 0)
        self.assertTrue(len(walking_paths.edges) > 0)

if __name__ == '__main__':
    unittest.main()