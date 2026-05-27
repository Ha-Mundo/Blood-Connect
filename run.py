""" Entry point for the application """
import os
import logging
from app import create_app
from app.extensions import db
from create_admin import create_admin

app = create_app()

with app.app_context():
    # Ensure database tables are created on the target database (SQLite or Neon PostgreSQL)
    db.create_all() 
    
    # Check the running environment
    is_production = os.getenv("FLASK_ENV") == "production"
    
    if is_production:
        # Production mode: Automatically trigger admin creation from env variables
        try:
            create_admin()
        except Exception as e:
            app.logger.error(f"Error during production auto-admin creation: {e}")
    else:
        # Local development mode: Skip automatic execution to prevent interactive prompt blocks
        print("--- Local Development Mode ---")
        print("To create an admin user locally, run: python create_admin.py")
        print("To create sample data locally, run: python seed_data.py")
        
if __name__ == '__main__':
    # Run with debug mode enabled only in local development
    is_production = os.getenv("FLASK_ENV") == "production"
    app.run(debug=not is_production)