import unittest
import json
from app import app, db
from models.models import Claim, Owner, Holder, ClaimStatusEnum

class ClaimsAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and in-memory database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test owner
            owner = Owner(
                first_name='John',
                last_name='Doe',
                email='john@example.com'
            )
            db.session.add(owner)
            
            # Create test holder
            holder = Holder(
                holder_name='Test Holder Inc',
                holder_type='Bank',
                contact_email='holder@example.com'
            )
            db.session.add(holder)
            db.session.commit()
            
            self.owner_id = owner.id
            self.holder_id = holder.id

    def tearDown(self):
        """Clean up database after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_claim(self):
        """Test POST /api/claims - Create new claim"""
        claim_data = {
            'claim_number': 'CLM-001',
            'owner_id': self.owner_id,
            'holder_id': self.holder_id,
            'property_type': 'Bank Account',
            'reported_value': 1500.50,
            'reporting_state': 'TX'
        }
        
        response = self.app.post(
            '/api/claims',
            data=json.dumps(claim_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_create_claim_missing_fields(self):
        """Test POST /api/claims - Missing required fields"""
        claim_data = {
            'claim_number': 'CLM-002',
            # Missing required fields
        }
        
        response = self.app.post(
            '/api/claims',
            data=json.dumps(claim_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_claim(self):
        """Test GET /api/claims/<id> - Get claim by ID"""
        # First create a claim
        with app.app_context():
            claim = Claim(
                claim_number='CLM-003',
                owner_id=self.owner_id,
                holder_id=self.holder_id,
                property_type='Savings Account',
                reported_value=2500.00,
                reporting_state='CA',
                claim_status=ClaimStatusEnum.submitted
            )
            db.session.add(claim)
            db.session.commit()
            claim_id = claim.id

        response = self.app.get(f'/api/claims/{claim_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['claim_number'], 'CLM-003')
        self.assertEqual(data['property_type'], 'Savings Account')

    def test_get_claim_not_found(self):
        """Test GET /api/claims/<id> - Claim not found"""
        response = self.app.get('/api/claims/99999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_update_claim(self):
        """Test PUT /api/claims/<id> - Update claim"""
        # First create a claim
        with app.app_context():
            claim = Claim(
                claim_number='CLM-004',
                owner_id=self.owner_id,
                holder_id=self.holder_id,
                property_type='Investment Account',
                reported_value=5000.00,
                reporting_state='NY',
                claim_status=ClaimStatusEnum.submitted
            )
            db.session.add(claim)
            db.session.commit()
            claim_id = claim.id

        update_data = {
            'claim_status': 'under_review',
            'reported_value': 5500.00
        }
        
        response = self.app.put(
            f'/api/claims/{claim_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.app.get(f'/api/claims/{claim_id}')
        data = json.loads(response.data)
        self.assertEqual(data['claim_status'], 'under_review')

    def test_delete_claim(self):
        """Test DELETE /api/claims/<id> - Delete claim"""
        # First create a claim
        with app.app_context():
            claim = Claim(
                claim_number='CLM-005',
                owner_id=self.owner_id,
                holder_id=self.holder_id,
                property_type='Checking Account',
                reported_value=750.00,
                reporting_state='FL',
                claim_status=ClaimStatusEnum.submitted
            )
            db.session.add(claim)
            db.session.commit()
            claim_id = claim.id

        response = self.app.delete(f'/api/claims/{claim_id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        response = self.app.get(f'/api/claims/{claim_id}')
        self.assertEqual(response.status_code, 404)

    def test_list_claims(self):
        """Test GET /api/claims - List all claims"""
        # Create multiple claims
        with app.app_context():
            for i in range(3):
                claim = Claim(
                    claim_number=f'CLM-LIST-{i}',
                    owner_id=self.owner_id,
                    holder_id=self.holder_id,
                    property_type='Test Account',
                    reported_value=1000.00 * (i + 1),
                    reporting_state='TX',
                    claim_status=ClaimStatusEnum.submitted
                )
                db.session.add(claim)
            db.session.commit()

        response = self.app.get('/api/claims')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('claims', data)
        self.assertGreaterEqual(len(data['claims']), 3)

    def test_list_claims_with_filter(self):
        """Test GET /api/claims?reporting_state=TX - Filter claims by state"""
        # Create claims with different states
        with app.app_context():
            for state in ['TX', 'CA', 'NY']:
                claim = Claim(
                    claim_number=f'CLM-{state}-001',
                    owner_id=self.owner_id,
                    holder_id=self.holder_id,
                    property_type='Test Account',
                    reported_value=1000.00,
                    reporting_state=state,
                    claim_status=ClaimStatusEnum.submitted
                )
                db.session.add(claim)
            db.session.commit()

        response = self.app.get('/api/claims?reporting_state=TX')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('claims', data)
        # Verify all returned claims are from TX
        for claim in data['claims']:
            self.assertEqual(claim['reporting_state'], 'TX')

if __name__ == '__main__':
    unittest.main()
