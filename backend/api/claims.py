from flask import Blueprint, request, jsonify
from models.models import Claim, ClaimStatusEnum
from db import db
from sqlalchemy.exc import IntegrityError

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('', methods=['POST'])
def create_claim():
    data = request.get_json()
    required_fields = ['claim_number', 'owner_id', 'holder_id', 'property_type', 'reported_value', 'reporting_state']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    claim = Claim(
        claim_number=data['claim_number'],
        owner_id=data['owner_id'],
        holder_id=data['holder_id'],
        property_type=data['property_type'],
        reported_value=data['reported_value'],
        reporting_state=data['reporting_state'],
        dormancy_date=data.get('dormancy_date'),
        due_diligence_deadline=data.get('due_diligence_deadline'),
        claim_status=ClaimStatusEnum.submitted
    )
    try:
        db.session.add(claim)
        db.session.commit()
        return jsonify({'id': claim.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Claim could not be created'}), 500

@claims_bp.route('/<int:claim_id>', methods=['GET'])
def get_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    return jsonify({
        'id': claim.id,
        'claim_number': claim.claim_number,
        'owner_id': claim.owner_id,
        'holder_id': claim.holder_id,
        'property_type': claim.property_type,
        'reported_value': claim.reported_value,
        'claim_status': claim.claim_status.value,
        'reporting_state': claim.reporting_state,
        'dormancy_date': claim.dormancy_date.isoformat() if claim.dormancy_date else None,
        'due_diligence_deadline': claim.due_diligence_deadline.isoformat() if claim.due_diligence_deadline else None
    })

@claims_bp.route('/<int:claim_id>', methods=['PUT', 'PATCH'])
def update_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    data = request.get_json()
    for field in ['claim_number', 'owner_id', 'holder_id', 'property_type', 'reported_value', 'reporting_state', 'claim_status', 'dormancy_date', 'due_diligence_deadline']:
        if field in data:
            setattr(claim, field, data[field])
    try:
        db.session.commit()
        return jsonify({'message': 'Claim updated successfully'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Could not update claim'}), 500

@claims_bp.route('/<int:claim_id>', methods=['DELETE'])
def delete_claim(claim_id):
    claim = Claim.query.get(claim_id)
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    try:
        db.session.delete(claim)
        db.session.commit()
        return jsonify({'message': 'Claim deleted successfully'})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not delete claim'}), 500

@claims_bp.route('', methods=['GET'])
def list_claims():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    
    query = Claim.query.order_by(Claim.claim_number.asc())
    reporting_state = request.args.get('reporting_state')
    if reporting_state:
        query = query.filter_by(reporting_state=reporting_state)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    claims = pagination.items
    
    results = []
    for claim in claims:
        results.append({
            'id': claim.id,
            'claim_number': claim.claim_number,
            'owner_id': claim.owner_id,
            'holder_id': claim.holder_id,
            'property_type': claim.property_type,
            'reported_value': claim.reported_value,
            'claim_status': claim.claim_status.value,
            'reporting_state': claim.reporting_state,
            'dormancy_date': claim.dormancy_date.isoformat() if claim.dormancy_date else None,
            'due_diligence_deadline': claim.due_diligence_deadline.isoformat() if claim.due_diligence_deadline else None,
        })
    
    return jsonify({
        'claims': results,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })
