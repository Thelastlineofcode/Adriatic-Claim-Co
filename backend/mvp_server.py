"""
Minimal Flask server stub for MVP claim intake.

Usage (from repo root):
  python3 backend/mvp_server.py

This will run a simple server on port 5001 with an endpoint POST /api/claims
which writes incoming claims to backend/data/claims.json and returns a simple
calculation applying the Texas 10% contingency cap.

This is a development stub only — do not use in production without security, rate-limiting,
validation, and legal review.
"""
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CLAIMS_FILE = os.path.join(DATA_DIR, 'claims.json')

def _append_claim(record):
    records = []
    if os.path.exists(CLAIMS_FILE):
        try:
            with open(CLAIMS_FILE, 'r') as f:
                records = json.load(f)
        except Exception:
            records = []
    records.append(record)
    with open(CLAIMS_FILE, 'w') as f:
        json.dump(records, f, indent=2)

@app.route('/api/claims', methods=['POST'])
def create_claim():
    data = request.get_json(force=True)
    # Basic validation (expand as needed)
    name = data.get('name')
    claim_amount = float(data.get('claim_amount') or 0)
    flat_fee = data.get('flat_fee')

    if not name or claim_amount <= 0:
        return jsonify({'error': 'name and positive claim_amount required'}), 400

    # Apply Texas contingency cap (10%) for net calculation
    contingency_rate = 0.10
    contingency_fee = round(claim_amount * contingency_rate, 2)
    net_contingency = round(claim_amount - contingency_fee, 2)
    net_flat = None
    if flat_fee:
        net_flat = round(claim_amount - float(flat_fee), 2)

    response = {
        'name': name,
        'gross': claim_amount,
        'contingency_fee': contingency_fee,
        'net_contingency': net_contingency,
        'flat_fee': float(flat_fee) if flat_fee else None,
        'net_flat': net_flat,
        'net': net_flat if (net_flat is not None and net_flat > net_contingency) else net_contingency,
        'message': 'Claim recorded (Adriatic Claim Co development stub).'
    }

    # redact sensitive fields before saving
    to_save = dict(data)
    if 'email' in to_save:
        to_save['email'] = to_save['email']
    # Do not store full SSN in this stub; if provided, redact
    if 'ssn' in to_save:
        to_save['ssn'] = 'REDACTED'

    # annotate saved record with handler information
    to_save.update({'calculation': response, 'handled_by': 'Adriatic Claim Co (MVP stub)'})
    _append_claim(to_save)

    return jsonify(response)


@app.route('/api/admin/claims', methods=['GET'])
def list_claims():
    """Development-only endpoint: return stored claims as JSON.

    WARNING: This endpoint is not authenticated. Only use locally or behind
    proper access controls in staging/production.
    """
    if not os.path.exists(CLAIMS_FILE):
        return jsonify([])
    try:
        with open(CLAIMS_FILE, 'r') as f:
            records = json.load(f)
    except Exception:
        records = []
    return jsonify(records)

if __name__ == '__main__':
    # Run on port 5001 to avoid conflict with other services
    app.run(host='127.0.0.1', port=5001, debug=True)
