import sys

from cafe_pos.database import SessionLocal
from cafe_pos.models.user import User, UserRole
from cafe_pos.services.auth_service import hash_password

if len(sys.argv) != 3:
    print("Використання: python -m cafe_pos.create_admin <email> <пароль>")
    sys.exit(1)

email, password = sys.argv[1], sys.argv[2]

db = SessionLocal()
admin = User(email=email, hashed_password=hash_password(password), role=UserRole.admin)
db.add(admin)
db.commit()
print(f"Адміна {email} створено")
db.close()
