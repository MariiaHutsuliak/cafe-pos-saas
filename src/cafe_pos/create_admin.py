from cafe_pos.database import SessionLocal
from cafe_pos.models.user import User, UserRole
from cafe_pos.services.auth_service import hash_password

email = input("Email адміна: ")
password = input("Пароль адміна: ")

db = SessionLocal()
admin = User(email=email, hashed_password=hash_password(password), role=UserRole.admin)
db.add(admin)
db.commit()
print(f"Адміна {email} створено")
db.close()
