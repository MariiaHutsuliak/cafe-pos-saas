import random
from datetime import datetime, timedelta, timezone

from cafe_pos.database import SessionLocal
from cafe_pos.models.product import Product
from cafe_pos.models.sale import Sale

CAFES = ["Кав'ярня на Хрещатику", "Кав'ярня Поділ", "Кав'ярня Оболонь"]
DEMO_PRODUCTS = [
    ("Капучино", "Напій", 65),
    ("Лате", "Напій", 70),
    ("Американо", "Напій", 50),
    ("Круасан", "Десерт", 55),
    ("Чізкейк", "Десерт", 85),
]

db = SessionLocal()

products = db.query(Product).all()
if not products:
    for name, category, price in DEMO_PRODUCTS:
        db.add(Product(name=name, category=category, price=price))
    db.commit()
    products = db.query(Product).all()

now = datetime.now(timezone.utc)
created = 0
for day_offset in range(14):
    day = now - timedelta(days=day_offset)
    for _ in range(random.randint(15, 40)):
        product = random.choice(products)
        quantity = random.randint(1, 3)
        sale_time = day.replace(
            hour=random.randint(7, 20), minute=random.randint(0, 59)
        )
        db.add(
            Sale(
                product_id=product.id,
                cafe_name=random.choice(CAFES),
                quantity=quantity,
                total_price=round(product.price * quantity, 2),
                created_at=sale_time,
            )
        )
        created += 1

db.commit()
db.close()
print(f"Створено {created} демо-продажів за останні 14 днів")
