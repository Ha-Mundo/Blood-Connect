from app import app, db, User, BloodDonation, bcrypt
import datetime

def seed():
    with app.app_context():
        # Ensure tables exist before seeding
        db.create_all()
        
        today = datetime.date.today()
        next_d = today + datetime.timedelta(days=90)
        default_pw = bcrypt.generate_password_hash("Password123!").decode('utf-8')

        # 1. User-Test (Standard User)
        if not User.query.filter_by(email="test@mail.com").first():
            db.session.add(User(
                username="User-Test", 
                email="test@mail.com", 
                password=default_pw, 
                role="user",
                is_verified=True,
                blood_group="o+"
            ))

        # 2. Donors data
        donors_data = [
            {"name": "julia", "age": 25, "blood_groups": "a+", "city": "edinburgh", "email": "julia@mail.com"},
            {"name": "michelle", "age": 23, "blood_groups": "o-", "city": "edinburgh", "email": "michelle@mail.com"},
            {"name": "ana", "age": 35, "blood_groups": "o-", "city": "edinburgh", "email": "ana@mail.com"},
            {"name": "yiming", "age": 32, "blood_groups": "o-", "city": "edinburgh", "email": "yiming@mail.com"},
            {"name": "kristina", "age": 27, "blood_groups": "o-", "city": "brisbane", "email": "kristy@mail.com"},
            {"name": "marco", "age": 29, "blood_groups": "b+", "city": "roma", "email": "marco@mail.com"},
            {"name": "elena", "age": 31, "blood_groups": "ab-", "city": "roma", "email": "elena@mail.com"},
            {"name": "stefano", "age": 45, "blood_groups": "a-", "city": "milano", "email": "stefano@mail.com"},
            {"name": "clara", "age": 22, "blood_groups": "o+", "city": "milano", "email": "clara@mail.com"},
            {"name": "robert", "age": 38, "blood_groups": "b-", "city": "edinburgh", "email": "rob@mail.com"},
            {"name": "lisa", "age": 26, "blood_groups": "a+", "city": "brisbane", "email": "lisa@mail.com"},
            {"name": "kristal", "age": 30, "blood_groups": "o+", "city": "brisbane", "email": "kristal@mail.com"},
            {"name": "sophie", "age": 24, "blood_groups": "ab+", "city": "london", "email": "sophie@mail.com"},
            {"name": "james", "age": 40, "blood_groups": "o-", "city": "london", "email": "james@mail.com"},
            {"name": "yuki", "age": 28, "blood_groups": "b+", "city": "tokyo", "email": "yuki@mail.com"},
            {"name": "diego", "age": 33, "blood_groups": "a-", "city": "madrid", "email": "diego@mail.com"},
            {"name": "sara", "age": 21, "blood_groups": "o+", "city": "roma", "email": "sara@mail.com"},
            {"name": "pavel", "age": 37, "blood_groups": "b-", "city": "prague", "email": "pavel@mail.com"},
            {"name": "nina", "age": 26, "blood_groups": "a+", "city": "milano", "email": "nina@mail.com"},
            {"name": "tom", "age": 50, "blood_groups": "o-", "city": "edinburgh", "email": "tom@mail.com"}
        ]

        # 3. Seeding loop for both Tables (User and BloodDonation)
        new_entries = 0
        for data in donors_data:
            # Check if User already exists to avoid duplicates
            if not User.query.filter_by(email=data['email']).first():
                # Create a pre-verified User account for each donor
                new_user = User(
                    username=data['name'],
                    email=data['email'],
                    password=default_pw,
                    role="user",
                    is_verified=True,
                    blood_group=data['blood_groups']
                )
                db.session.add(new_user)

            # Check if Donation record already exists
            if not BloodDonation.query.filter_by(email=data['email']).first():
                db.session.add(BloodDonation(
                    **data, 
                    latest_donation=today, 
                    next_donation=next_d, 
                    donation_counter=1,
                    status='Pending'
                ))
                new_entries += 1
        
        db.session.commit()
        print(f"Seed completed. New donation records added: {new_entries}")

if __name__ == "__main__":
    seed()