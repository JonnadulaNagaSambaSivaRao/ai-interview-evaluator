from app.database import SessionLocal

from app.models.user import User

from app.auth import hash_password


ADMIN_EMAIL = "admin@test.com"

ADMIN_PASSWORD = "Admin@12345"


db = SessionLocal()


existing_admin = db.query(
    User
).filter(
    User.email == ADMIN_EMAIL
).first()


if existing_admin:

    print("Admin already exists")

else:

    admin = User(
        name="Administrator",
        email=ADMIN_EMAIL,
        hashed_password=hash_password(
            ADMIN_PASSWORD
        ),
        role="admin"
    )

    db.add(admin)

    db.commit()

    print("Admin created successfully")
    print("Email:", ADMIN_EMAIL)
    print("Password:", ADMIN_PASSWORD)


db.close()