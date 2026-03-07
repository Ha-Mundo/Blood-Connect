from app import app, db, User, BloodDonation, bcrypt
import datetime

def seed():
    with app.app_context():
        db.create_all()
        today = datetime.date.today()
        next_d = today + datetime.timedelta(days=90)

        # 1. User-Test
        if not User.query.filter_by(email="test@mail.com").first():
            pw = bcrypt.generate_password_hash("password123").decode('utf-8')
            db.session.add(User(username="User-Test", email="test@mail.com", password=pw))

        # 2. Donors sata
        donors_data = [
            {"name": "julia", "age": 25, "blood_groups": "a+", "city": "edinburgh", "email": "julia@mail.com"},
            {"name": "michelle", "age": 23, "blood_groups": "0-", "city": "edinburgh", "email": "michelle@mail.com"},
            {"name": "ana", "age": 35, "blood_groups": "0-", "city": "edinburgh", "email": "ana@mail.com"},
            {"name": "yiming", "age": 32, "blood_groups": "0-", "city": "edinburgh", "email": "yiming@mail.com"},
            {"name": "kristina", "age": 27, "blood_groups": "0-", "city": "brisbane", "email": "kristy@mail.com"},
            {"name": "marco", "age": 29, "blood_groups": "b+", "city": "roma", "email": "marco@mail.com"},
            {"name": "elena", "age": 31, "blood_groups": "ab-", "city": "roma", "email": "elena@mail.com"},
            {"name": "stefano", "age": 45, "blood_groups": "a-", "city": "milano", "email": "stefano@mail.com"},
            {"name": "clara", "age": 22, "blood_groups": "0+", "city": "milano", "email": "clara@mail.com"},
            {"name": "robert", "age": 38, "blood_groups": "b-", "city": "edinburgh", "email": "rob@mail.com"},
            {"name": "lisa", "age": 26, "blood_groups": "a+", "city": "brisbane", "email": "lisa@mail.com"},
            {"name": "ahmed", "age": 30, "blood_groups": "0+", "city": "brisbane", "email": "ahmed@mail.com"},
            {"name": "sophie", "age": 24, "blood_groups": "ab+", "city": "london", "email": "sophie@mail.com"},
            {"name": "james", "age": 40, "blood_groups": "0-", "city": "london", "email": "james@mail.com"},
            {"name": "yuki", "age": 28, "blood_groups": "b+", "city": "tokyo", "email": "yuki@mail.com"},
            {"name": "diego", "age": 33, "blood_groups": "a-", "city": "madrid", "email": "diego@mail.com"},
            {"name": "sara", "age": 21, "blood_groups": "0+", "city": "roma", "email": "sara@mail.com"},
            {"name": "pavel", "age": 37, "blood_groups": "b-", "city": "prague", "email": "pavel@mail.com"},
            {"name": "nina", "age": 26, "blood_groups": "a+", "city": "milano", "email": "nina@mail.com"},
            {"name": "tom", "age": 50, "blood_groups": "0-", "city": "edinburgh", "email": "tom@mail.com"}
        ]

        # 3. Seeding loop
        new_entries = 0
        for data in donors_data:
            if not BloodDonation.query.filter_by(email=data['email']).first():
                db.session.add(BloodDonation(**data, latest_donation=today, next_donation=next_d))
                new_entries += 1
        
        db.session.commit()
        print(f"Seed completed. New records added!: {new_entries}")

if __name__ == "__main__":
    seed()