from app.services import app, db, User, bcrypt
import getpass

def create_admin():
    """ Script to create an administrative user via terminal """
    with app.app_context():
        # 1. DATABASE INITIALIZATION
        # Ensure tables exist before attempting to insert data
        db.create_all()

        print("--- Create Super User (Admin) ---")
        username = input("Enter username: ")
        email = input("Enter email: ") # Required by the User model
        
        # 2. DUPLICATE CHECK
        # Verify if the username or email is already taken
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            print("Error: User with this username or email already exists.")
            return

        # 3. SECURE PASSWORD INPUT
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        # 4. PASSWORD HASHING
        # Securely hash the password before storage
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # 5. OBJECT CREATION
        # Assign 'admin' role to grant elevated permissions
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
            # Rollback in case of database errors
            db.session.rollback()
            print(f"\nDATABASE ERROR: {e}")

if __name__ == "__main__":
    create_admin()