from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin=User.query.filter_by(role="Admin").first()

    if admin is None:
        admin=User(username="admin",email="admin@trek.com",password=generate_password_hash("admin123"),
        role="Admin",status="ACTIVE")
        db.session.add(admin)
        db.session.commit()

        print("✅ Admin created successfully!")

    else:
        print("⚠️ Admin already exists!")