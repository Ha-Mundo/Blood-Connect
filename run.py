""" Entry point for the application """
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
        # Ensure database tables are created
        db.create_all() 
        
if __name__ == '__main__':
    app.run(debug=True)