from flask import Flask, jsonify
from db import db
from flask_cors import CORS
from datetime import datetime
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


app = Flask(__name__)

# Configure CORS for production
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Update with your frontend domain in production
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database configuration - handles both PostgreSQL and SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///adriatic_claims.db')
# Fix for Heroku/Render PostgreSQL URL (postgres:// -> postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
db.init_app(app)


from api.owners import owners_bp
app.register_blueprint(owners_bp)

from api.claims import claims_bp
app.register_blueprint(claims_bp)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'development')
    })

@app.route('/')
def index():
    return jsonify({
        'message': 'Adriatic Claim Co API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'owners': '/api/owners',
            'claims': '/api/claims'
        }
    })

# Create tables on startup (for SQLite in development)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') != 'production')
