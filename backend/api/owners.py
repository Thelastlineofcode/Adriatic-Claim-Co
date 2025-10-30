from flask import Blueprint, request, jsonify
from models.models import Owner
from db import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

owners_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

@owners_bp.route('', methods=['POST'])
def create_owner():
    data = request.get_json()
    if not data or 'first_name' not in data or 'last_name' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Normalize types where needed
    dob = data.get('date_of_birth')
    if isinstance(dob, str) and dob:
        try:
            # Accept YYYY-MM-DD (HTML date input)
            dob = datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            # Try full ISO format as fallback
            try:
                dob = datetime.fromisoformat(dob)
            except ValueError:
                return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD'}), 400

    owner = Owner(
        first_name=data['first_name'],
        last_name=data['last_name'],
        middle_name=data.get('middle_name'),
        date_of_birth=dob,
        ssn=data.get('ssn'),
        tax_id=data.get('tax_id'),
        email=data.get('email'),
        phone=data.get('phone'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        country=data.get('country'),
    )
    try:
        db.session.add(owner)
        db.session.commit()
        return jsonify({'id': owner.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Owner could not be created'}), 500

@owners_bp.route('/<int:owner_id>', methods=['GET'])
def get_owner(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({'error': 'Owner not found'}), 404
    return jsonify({
        'id': owner.id,
        'first_name': owner.first_name,
        'last_name': owner.last_name,
        'middle_name': owner.middle_name,
        'email': owner.email,
        'phone': owner.phone,
        'address_line1': owner.address_line1,
        'address_line2': owner.address_line2,
        'city': owner.city,
        'state': owner.state,
        'postal_code': owner.postal_code,
        'country': owner.country,
    })

# Additional routes (optional) could include update_owner, delete_owner, list_owners for full CRUD
@owners_bp.route('/<int:owner_id>', methods=['PUT', 'PATCH'])
def update_owner(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({'error': 'Owner not found'}), 404

    data = request.get_json()
    for field in ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'ssn', 'tax_id', 'email',
                  'phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']:
        if field in data:
            setattr(owner, field, data[field])
    try:
        db.session.commit()
        return jsonify({'message': 'Owner updated successfully'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Could not update owner'}), 500

@owners_bp.route('/<int:owner_id>', methods=['DELETE'])
def delete_owner(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({'error': 'Owner not found'}), 404
    try:
        db.session.delete(owner)
        db.session.commit()
        return jsonify({'message': 'Owner deleted successfully'})
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not delete owner'}), 500

@owners_bp.route('', methods=['GET'])
def list_owners():
    # Simple pagination: ?page=1&per_page=20
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)

    owners_query = Owner.query.order_by(Owner.last_name.asc(), Owner.first_name.asc())
    pagination = owners_query.paginate(page=page, per_page=per_page, error_out=False)
    owners = pagination.items

    results = []
    for owner in owners:
        results.append({
            'id': owner.id,
            'first_name': owner.first_name,
            'last_name': owner.last_name,
            'email': owner.email,
            'phone': owner.phone,
            'state': owner.state,
        })

    return jsonify({
        'owners': results,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })
