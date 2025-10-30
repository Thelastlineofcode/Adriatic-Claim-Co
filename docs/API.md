# API Reference

Base URL: Depends on environment

- Local: http://localhost:5000
- Production: https://your-backend-url.onrender.com

All endpoints return JSON.

## Health

GET /health

Response 200:
{
"status": "ok",
"timestamp": "2025-01-01T00:00:00.000000",
"environment": "development|production"
}

GET /

Response 200:
{
"message": "Adriatic Claim Co API",
"version": "1.0.0",
"endpoints": {
"health": "/health",
"owners": "/api/owners",
"claims": "/api/claims"
}
}

## Owners

### Create Owner

POST /api/owners

Request Body (JSON):
{
"first_name": "Ada",
"last_name": "Lovelace",
"email": "ada@example.com",
"phone": "+1 555-123-4567",
"date_of_birth": "1980-02-01", // YYYY-MM-DD
"address_line1": "123 Main St",
"city": "Austin",
"state": "TX"
}

Response 201:
{ "id": 1 }

Response 400:
{ "error": "Missing required fields" }

Response 500:
{ "error": "Owner could not be created" }

### Get Owner

GET /api/owners/{id}

Response 200:
{
"id": 1,
"first_name": "Ada",
"last_name": "Lovelace",
"middle_name": null,
"email": "ada@example.com",
"phone": "+1 555-123-4567",
"address_line1": "123 Main St",
"address_line2": null,
"city": "Austin",
"state": "TX",
"postal_code": null,
"country": null
}

Response 404:
{ "error": "Owner not found" }

### List Owners

GET /api/owners?page=1&per_page=20

Response 200:
{
"owners": [ { "id": 1, "first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com", "phone": "+1 555-123-4567", "state": "TX" } ],
"total": 1,
"page": 1,
"pages": 1
}

### Update Owner

PUT /api/owners/{id}

Request Body: Partial or full owner object

Response 200:
{ "message": "Owner updated successfully" }

Response 404:
{ "error": "Owner not found" }

### Delete Owner

DELETE /api/owners/{id}

Response 200:
{ "message": "Owner deleted successfully" }

Response 404:
{ "error": "Owner not found" }

## Claims

### Create Claim

POST /api/claims

Request Body:
{
"claim_number": "CLM-0001",
"owner_id": 1,
"holder_id": 1,
"property_type": "unclaimed_property",
"reported_value": 123.45,
"reporting_state": "TX",
"dormancy_date": "2024-12-31T00:00:00",
"due_diligence_deadline": "2025-03-31T00:00:00"
}

Response 201:
{ "id": 1 }

Response 400:
{ "error": "Missing required field: claim_number" }

### Get Claim

GET /api/claims/{id}

Response 200:
{
"id": 1,
"claim_number": "CLM-0001",
"owner_id": 1,
"holder_id": 1,
"property_type": "unclaimed_property",
"reported_value": 123.45,
"claim_status": "submitted",
"reporting_state": "TX",
"dormancy_date": null,
"due_diligence_deadline": null
}

Response 404:
{ "error": "Claim not found" }

### List Claims

GET /api/claims?page=1&per_page=20&reporting_state=TX

Response 200:
{
"claims": [ { "id": 1, "claim_number": "CLM-0001", "owner_id": 1, "holder_id": 1, "property_type": "unclaimed_property", "reported_value": 123.45, "claim_status": "submitted", "reporting_state": "TX", "dormancy_date": null, "due_diligence_deadline": null } ],
"total": 1,
"page": 1,
"pages": 1
}

### Update Claim

PUT /api/claims/{id}

Response 200:
{ "message": "Claim updated successfully" }

### Delete Claim

DELETE /api/claims/{id}

Response 200:
{ "message": "Claim deleted successfully" }

## CORS

CORS is configured to allow localhost and Firebase Hosting domains by default. In production, set `CORS_ALLOWED_ORIGINS` to a comma-separated list of allowed origins.
