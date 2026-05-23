import os
import getpass
from app import create_app
from app.extensions import db, bcrypt
from app.models import User

app = create_app()

def create_admin():
    """Dynamic script to create an administrator user (Local or Production)"""
    with app.app_context():
        # 1. DATABASE INITIALIZATION
        db.create_all()

        # Check if we are in production by reading environment variables
        env_username = os.getenv("ADMIN_USERNAME")
        env_email = os.getenv("ADMIN_EMAIL")
        env_password = os.getenv("ADMIN_PASSWORD")

        # If ALL environment variables are present, use automated mode (Production)
        if env_username and env_email and env_password:
            print("--- Creating Admin from Environment Variables (Production) ---")
            username = env_username
            email = env_email
            password = env_password
        else:
            # Otherwise, switch to interactive mode (Local)
            print("--- Interactive Super User Creation (Local) ---")
            username = input("Enter username: ")
            email = input("Enter email: ")
            
            password = getpass.getpass("Enter password: ")
            confirm_password = getpass.getpass("Confirm password: ")

            if password != confirm_password:
                print("Error: Passwords do not match.")
                return

        # 2. DUPLICATE CHECK
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            print(f"Notice: User with username '{username}' or email '{email}' already exists. Skipping creation.")
            return

        # 3. PASSWORD HASHING
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 4. OBJECT CREATION
        new_user = User(
            username=username, 
            email=email.lower(), 
            password=hashed_pw,
            role='admin', 
            is_verified=True
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"\nSUCCESS: Admin '{username}' created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"\nDATABASE ERROR: {e}")

if __name__ == "__main__":
    create_admin()