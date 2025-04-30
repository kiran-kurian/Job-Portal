from app import app, db, User
from werkzeug.security import generate_password_hash

def register_admin():
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")

    hashed_pw = generate_password_hash(password)

    with app.app_context():
        admin = User(username=username, password=hashed_pw, email=email, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully.")

if __name__ == '__main__':
    register_admin()