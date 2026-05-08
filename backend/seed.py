"""Seed to populate the database with sample data for testing. Run: python seed.py"""
from app import create_app, db
from app.models.user import User
from app.models.profile import Profile, Interest
from datetime import date

app = create_app()

INTERESTS = [
    'hiking', 'photography', 'gaming', 'cooking', 'travel',
    'music', 'reading', 'fitness', 'art', 'movies',
    'dancing', 'yoga', 'cycling', 'surfing', 'coffee'
]

USERS = [
    {
        'email': 'alice@example.com', 'username': 'alice_w', 'password': 'password123',
        'first_name': 'Alice', 'last_name': 'Wonder', 'dob': date(1999, 3, 15),
        'gender': 'female', 'looking_for': 'male', 'bio': 'Love hiking and adventure! Let\'s explore the world together.',
        'city': 'Kingston', 'country': 'Jamaica', 'latitude': 17.9970, 'longitude': -76.7936,
        'occupation': 'Teacher', 'education_level': 'bachelor',
        'interests': ['hiking', 'photography', 'travel', 'yoga', 'coffee']
    },
    {
        'email': 'bob@example.com', 'username': 'bob_builder', 'password': 'password123',
        'first_name': 'Bob', 'last_name': 'Builder', 'dob': date(1997, 7, 22),
        'gender': 'male', 'looking_for': 'female', 'bio': 'Software developer by day, photographer by night.',
        'city': 'Kingston', 'country': 'Jamaica', 'latitude': 17.9970, 'longitude': -76.7936,
        'occupation': 'Software Developer', 'education_level': 'master',
        'interests': ['photography', 'gaming', 'hiking', 'cycling', 'coffee']
    },
    {
        'email': 'grace@example.com', 'username': 'grace_g', 'password': 'password123',
        'first_name': 'Grace', 'last_name': 'Gamer', 'dob': date(2000, 11, 5),
        'gender': 'female', 'looking_for': 'any', 'bio': 'Gamer and coffee enthusiast. Let\'s play!',
        'city': 'Montego Bay', 'country': 'Jamaica', 'latitude': 18.4762, 'longitude': -77.8939,
        'occupation': 'Game Designer', 'education_level': 'bachelor',
        'interests': ['gaming', 'coffee', 'movies', 'music', 'art']
    },
    {
        'email': 'carol@example.com', 'username': 'carol_cook', 'password': 'password123',
        'first_name': 'Carol', 'last_name': 'Cook', 'dob': date(1998, 6, 18),
        'gender': 'female', 'looking_for': 'male', 'bio': 'Chef and coffee lover. Looking for someone to cook for!',
        'city': 'Portmore', 'country': 'Jamaica', 'latitude': 17.9500, 'longitude': -76.8833,
        'occupation': 'Chef', 'education_level': 'other',
        'interests': ['cooking', 'travel', 'music', 'fitness', 'dancing']
    },
    {
        'email': 'emma@example.com', 'username': 'emma_artist', 'password': 'password123',
        'first_name': 'Emma', 'last_name': 'Artist', 'dob': date(2001, 2, 28),
        'gender': 'female', 'looking_for': 'any', 'bio': 'Artist and creative soul. Let\'s create art together!',
        'city': 'Spanish Town', 'country': 'Jamaica', 'latitude': 17.9916, 'longitude': -76.9559,
        'occupation': 'Artist', 'education_level': 'bachelor',
        'interests': ['art', 'music', 'reading', 'travel', 'photography']
    },
]

def seed():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("Database tables created.")

        # Create interests
        interest_objs = {}
        for name in INTERESTS:
            i = Interest(name=name)
            db.session.add(i)
            interest_objs[name] = i
        db.session.commit()
        print(f"Created {len(INTERESTS)} interests.")

        # Create users and profiles
        for u_data in USERS:
            # Create user - adjust fields based on your User model
            # If your User model has 'name' field, include it; otherwise remove it
            user = User(
                email=u_data['email'], 
                username=u_data['username']
                # Remove 'name' if your User model doesn't have it
                # If your model has 'first_name' and 'last_name' in User, add them
            )
            user.set_password(u_data['password'])
            db.session.add(user)
            db.session.flush()  # Get user.id

            # Create profile
            profile = Profile(
                user_id=user.id,
                first_name=u_data['first_name'],
                last_name=u_data['last_name'],
                date_of_birth=u_data['dob'],
                gender=u_data['gender'],
                looking_for=u_data['looking_for'],
                bio=u_data['bio'],
                city=u_data['city'],
                country=u_data['country'],
                latitude=u_data['latitude'],
                longitude=u_data['longitude'],
                occupation=u_data['occupation'],
                education_level=u_data['education_level'],
                is_public=True,
                min_age_preference=18,
                max_age_preference=35,
                max_distance_km=200,
            )
            
            # Add interests to profile
            for iname in u_data['interests']:
                profile.interests.append(interest_objs[iname])

            db.session.add(profile)

        db.session.commit()
        print(f"Created {len(USERS)} users with profiles.")
        print("\n✓ Test accounts created successfully!")
        print("\nTest accounts (email / password):")
        for u in USERS:
            print(f"  📧 {u['email']}  🔑 {u['password']}")
        print("\n⭐ Seeding complete!")

if __name__ == '__main__':
    seed()