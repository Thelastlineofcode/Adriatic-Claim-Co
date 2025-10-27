import unittest
from app import app

class HealthRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_route(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)

if __name__ == '__main__':
    unittest.main()
