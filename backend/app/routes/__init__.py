from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

# Add this root route
@main_bp.route('/')
def index():
    return jsonify({
        'message': 'DriftDater API is running!',
        'status': 'online',
        'endpoints': {
            'auth': '/api/auth/register, /api/auth/login',
            'profiles': '/api/profiles',
            'matches': '/api/matches',
            'search': '/api/search'
        }
    })


# Add a health check route
@main_bp.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'DriftDater API'})