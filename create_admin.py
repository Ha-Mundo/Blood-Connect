# create_admin.py
from app import app, db, User, bcrypt
import getpass

def create_admin():
    with app.app_context():
        # Check if an admin already exists to avoid duplicates
        if User.query.filter_by(username='admin').first():
            print("Admin user already exists.")
            return

        print("--- Create Super User ---")
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ") # Hides input in terminal
        
        # Hash the password before saving! Never store plain text.
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} created successfully!")

if __name__ == "__main__":
    create_admin()