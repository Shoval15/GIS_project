import unittest
import json
from app import app

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_bounds(self):
        test_data = {
            "polygon": [[35.1, 31.7], [35.2, 31.7], [35.2, 31.8], [35.1, 31.8]],
            "bounds": {
                "northEast": {"lat": 31.8, "lng": 35.2},
                "southWest": {"lat": 31.7, "lng": 35.1}
            },
            "projectStatus": "",
            "apartmentType": "existing",
            "distance": "0.93",
            "sqMeterPerResident": "3",
            "residentsPerApartment": "3.5"
        }
        response = self.app.post('/api/bounds', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        if data['status'] == 'success':
            self.assertIn('allocated_layer', data['response'])
            self.assertIn('allocation_stats', data['response'])
        else:
            self.assertIn('response', data)

if __name__ == '__main__':
    unittest.main()