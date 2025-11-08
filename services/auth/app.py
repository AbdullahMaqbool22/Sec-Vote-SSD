"""
Authentication Service - Handles user registration and login
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import os
import sys

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import db, init_db
from shared.auth_utils import generate_token
from shared.validators import validate_email, validate_username, validate_password, sanitize_input

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///auth.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database
init_db(app)


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth'}), 200


@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract and validate inputs
    username = sanitize_input(data.get('username', ''), 20)
    email = sanitize_input(data.get('email', ''), 120)
    password = data.get('password', '')
    
    # Validation
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if not validate_username(username):
        return jsonify({'error': 'Invalid username. Must be 3-20 alphanumeric characters'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters with letters and numbers'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.username)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = sanitize_input(data.get('username', ''), 20)
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Generate token
    token = generate_token(user.id, user.username)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'token': token
    }), 200


@app.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token (for inter-service communication)"""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Token is required'}), 400
    
    from shared.auth_utils import decode_token
    payload = decode_token(data['token'])
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    return jsonify({
        'valid': True,
        'user_id': payload['user_id'],
        'username': payload['username']
    }), 200


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
