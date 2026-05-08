import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models.profile import Profile, Interest
from app.utils.helpers import save_profile_picture, compute_match_score
from datetime import datetime

profiles_bp = Blueprint('profiles', __name__)


def get_or_create_interest(name):
    name = name.strip().lower()
    interest = Interest.query.filter_by(name=name).first()
    if not interest:
        interest = Interest(name=name)
        db.session.add(interest)
    return interest


@profiles_bp.route('', methods=['POST'])
@login_required
def create_profile():

    # --- DEBUG ---
    print(f"🔍 Profile creation attempt")
    print(f"   Current user: {current_user}")
    print(f"   User ID: {current_user.id if current_user.is_authenticated else 'Not authenticated'}")
    print(f"   Request headers: {dict(request.headers)}")
    print(f"   Cookies: {request.cookies}")
    #end DEBUG ---


    if current_user.profile:
        return jsonify({'error': 'Profile already exists'}), 409

    # Handle multipart form data
    data = request.form.to_dict()
    file = request.files.get('profile_picture')

    required = ['first_name', 'last_name', 'date_of_birth', 'gender']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    profile = Profile(
        user_id=current_user.id,
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        date_of_birth=dob,
        gender=data.get('gender', 'other'),
        looking_for=data.get('looking_for', 'any'),
        bio=data.get('bio', ''),
        city=data.get('city', ''),
        country=data.get('country', ''),
        occupation=data.get('occupation', ''),
        education_level=data.get('education_level', ''),
        is_public=data.get('is_public', 'true').lower() == 'true',
        min_age_preference=int(data.get('min_age_preference', 18)),
        max_age_preference=int(data.get('max_age_preference', 99)),
        max_distance_km=int(data.get('max_distance_km', 100)),
    )

    # Optional lat/lon
    if data.get('latitude'):
        profile.latitude = float(data['latitude'])
    if data.get('longitude'):
        profile.longitude = float(data['longitude'])

    # Interests
    interest_names = request.form.getlist('interests')
    if isinstance(interest_names, str):
        interest_names = [interest_names]
    for name in interest_names:
        if name:
            profile.interests.append(get_or_create_interest(name))

    # Profile picture
    if file and file.filename:
        filename = save_profile_picture(file)
        if filename:
            profile.profile_picture = filename

    db.session.add(profile)
    db.session.commit()
    return jsonify({'message': 'Profile created', 'profile': profile.to_dict(include_private=True)}), 201


@profiles_bp.route('/me', methods=['GET'])
@login_required
def get_my_profile():

    # --- DEBUG ---
    print("=" * 50)
    print("🔍 GET /api/profiles/me called")
    print(f"   Current user: {current_user}")
    print(f"   User authenticated: {current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else 'Unknown'}")
    print(f"   Request cookies: {request.cookies}")
    print(f"   Session: {dict(session) if hasattr(request, 'session') else 'No session'}")
    print("=" * 50)
    #end DEBUG ---


    profile = current_user.profile
    if not profile:
        return jsonify({'error': 'No profile found'}), 404
    return jsonify({'profile': profile.to_dict(include_private=True)}), 200


@profiles_bp.route('/me', methods=['PUT'])
@login_required
def update_my_profile():
    profile = current_user.profile
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    data = request.form.to_dict()
    file = request.files.get('profile_picture')

    if data.get('first_name'):
        profile.first_name = data['first_name'].strip()
    if data.get('last_name'):
        profile.last_name = data['last_name'].strip()
    if data.get('date_of_birth'):
        try:
            profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    if data.get('gender'):
        profile.gender = data['gender']
    if data.get('looking_for'):
        profile.looking_for = data['looking_for']
    if data.get('bio') is not None:
        profile.bio = data['bio']
    if data.get('city') is not None:
        profile.city = data['city']
    if data.get('country') is not None:
        profile.country = data['country']
    if data.get('occupation') is not None:
        profile.occupation = data['occupation']
    if data.get('education_level') is not None:
        profile.education_level = data['education_level']
    if data.get('is_public') is not None:
        profile.is_public = data['is_public'].lower() == 'true'
    if data.get('min_age_preference'):
        profile.min_age_preference = int(data['min_age_preference'])
    if data.get('max_age_preference'):
        profile.max_age_preference = int(data['max_age_preference'])
    if data.get('max_distance_km'):
        profile.max_distance_km = int(data['max_distance_km'])
    if data.get('latitude'):
        profile.latitude = float(data['latitude'])
    if data.get('longitude'):
        profile.longitude = float(data['longitude'])

    # Update interests if provided
    interest_names = request.form.getlist('interests')
    if interest_names and len(interest_names) > 0:
        try:
            # Clear existing interests
            profile.interests.clear()
            # Flush to execute the DELETE immediately
            db.session.flush()
            
            # Add new interests
            for name in interest_names:
                if name and name.strip():
                    interest = get_or_create_interest(name.strip().lower())
                    # Check not already in collection (should be empty, but safe)
                    if interest not in profile.interests:
                        profile.interests.append(interest)
            
            print(f"Updated interests for user {current_user.id}: {interest_names}")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating interests: {e}")
            return jsonify({'error': f'Failed to update interests: {str(e)}'}), 500

    if file and file.filename:
        # Remove old picture
        if profile.profile_picture:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture)
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = save_profile_picture(file)
        if filename:
            profile.profile_picture = filename

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'profile': profile.to_dict(include_private=True)}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error committing profile update: {e}")
        return jsonify({'error': f'Failed to save profile: {str(e)}'}), 500

@profiles_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    if not profile.is_public and profile.user_id != current_user.id:
        return jsonify({'error': 'Profile is private'}), 403

    # Include match score if viewing someone else
    data = profile.to_dict()
    if current_user.profile and profile.user_id != current_user.id:
        score = compute_match_score(current_user.profile, profile)
        data['match_score'] = score
    return jsonify({'profile': data}), 200


@profiles_bp.route('/picture/<filename>', methods=['GET'])
def get_picture(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@profiles_bp.route('/browse', methods=['GET'])
@login_required
def browse_profiles():
    """Return profiles the current user hasn't acted on yet, with match scores."""
    from app.models.match import Match

    my_profile = current_user.profile
    if not my_profile:
        return jsonify({'error': 'Create your profile first'}), 400

    # IDs already liked/passed
    acted_ids = {m.liked_id for m in current_user.likes_given}
    acted_ids.add(current_user.id)

    profiles = Profile.query.filter(
        Profile.user_id.notin_(acted_ids),
        Profile.is_public == True
    ).all()

    result = []
    for p in profiles:
        d = p.to_dict()
        d['match_score'] = compute_match_score(my_profile, p)
        result.append(d)

    # Sort by match score descending
    result.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({'profiles': result}), 200
