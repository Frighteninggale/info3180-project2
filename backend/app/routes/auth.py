from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Make username optional - use email username part if not provided
    required = ['email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    email = data['email'].strip().lower()
    name = data.get('name', '').strip()
    username = data.get('username', '').strip()
    password = data['password']

    # If name not provided, use part of email
    if not name:
        name = email.split('@')[0]
    
    # If username not provided, use name
    if not username:
        username = name

    # Validate email format
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email address'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    # Create user - REMOVE the 'name' parameter
    user = User(
        email=email,
        username=username
        # name=name  # ← REMOVE THIS LINE
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({
        'message': 'Registration successful', 
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    login_user(user, remember=True)
    has_profile = user.profile is not None
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'has_profile': has_profile
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    has_profile = current_user.profile is not None
    return jsonify({
        'user': current_user.to_dict(),
        'has_profile': has_profile
    }), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        has_profile = current_user.profile is not None
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict(),
            'has_profile': has_profile
        }), 200
    return jsonify({'authenticated': False}), 200
