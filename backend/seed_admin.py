from werkzeug.security import generate_password_hash
from app import app
from models import db, User

with app.app_context():
    db.create_all()
    if User.query.filter_by(email='admin@college.edu').first():
        print("Admin already exists")
    else:
        admin = User(
            name='Admin User',
            email='admin@college.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@college.edu / admin123")
        