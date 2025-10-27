import unittest
import json
from app import app, db
from models.models import Owner

class OwnersAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and in-memory database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up database after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_owner(self):
        """Test POST /api/owners - Create new owner"""
        owner_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'middle_name': 'Marie',
            'email': 'jane.smith@example.com',
            'phone': '555-123-4567',
            'address_line1': '123 Main St',
            'city': 'Austin',
            'state': 'TX',
            'postal_code': '78701'
        }
        
        response = self.app.post(
            '/api/owners',
            data=json.dumps(owner_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_create_owner_missing_required_fields(self):
        """Test POST /api/owners - Missing required fields"""
        owner_data = {
            'first_name': 'John'
            # Missing last_name
        }
        
        response = self.app.post(
            '/api/owners',
            data=json.dumps(owner_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_owner_minimal_data(self):
        """Test POST /api/owners - Only required fields"""
        owner_data = {
            'first_name': 'Bob',
            'last_name': 'Johnson'
        }
        
        response = self.app.post(
            '/api/owners',
            data=json.dumps(owner_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_get_owner(self):
        """Test GET /api/owners/<id> - Get owner by ID"""
        # First create an owner
        with app.app_context():
            owner = Owner(
                first_name='Alice',
                last_name='Williams',
                email='alice@example.com',
                phone='555-987-6543'
            )
            db.session.add(owner)
            db.session.commit()
            owner_id = owner.id

        response = self.app.get(f'/api/owners/{owner_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Alice')
        self.assertEqual(data['last_name'], 'Williams')
        self.assertEqual(data['email'], 'alice@example.com')

    def test_get_owner_not_found(self):
        """Test GET /api/owners/<id> - Owner not found"""
        response = self.app.get('/api/owners/99999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_update_owner(self):
        """Test PUT /api/owners/<id> - Update owner"""
        # First create an owner
        with app.app_context():
            owner = Owner(
                first_name='Charlie',
                last_name='Brown',
                email='charlie@example.com'
            )
            db.session.add(owner)
            db.session.commit()
            owner_id = owner.id

        update_data = {
            'email': 'charlie.brown@newdomain.com',
            'phone': '555-111-2222'
        }
        
        response = self.app.put(
            f'/api/owners/{owner_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.app.get(f'/api/owners/{owner_id}')
        data = json.loads(response.data)
        self.assertEqual(data['email'], 'charlie.brown@newdomain.com')
        self.assertEqual(data['phone'], '555-111-2222')

    def test_delete_owner(self):
        """Test DELETE /api/owners/<id> - Delete owner"""
        # First create an owner
        with app.app_context():
            owner = Owner(
                first_name='David',
                last_name='Miller',
                email='david@example.com'
            )
            db.session.add(owner)
            db.session.commit()
            owner_id = owner.id

        response = self.app.delete(f'/api/owners/{owner_id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        response = self.app.get(f'/api/owners/{owner_id}')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
