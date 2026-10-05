import random
from datetime import datetime, timedelta, timezone

from cafe_pos.database import SessionLocal
from cafe_pos.models.cafe import Cafe
from cafe_pos.models.product import Product
from cafe_pos.models.sale import Sale, SaleItem

CAFES = ["Кав'ярня на Хрещатику", "Кав'ярня Поділ", "Кав'ярня Оболонь"]
DEMO_PRODUCTS = [
    ("Капучино", "Напій", 65),
    ("Лате", "Напій", 70),
    ("Американо", "Напій", 50),
    ("Круасан", "Десерт", 55),
    ("Чізкейк", "Десерт", 85),
]

db = SessionLocal()

if db.query(Sale).count() > 0:
    print("Демо-дані вже є, нічого не створюю.")
    db.close()
    raise SystemExit

products = db.query(Product).all()
if not products:
    for name, category, price in DEMO_PRODUCTS:
        db.add(Product(name=name, category=category, price=price))
    db.commit()
    products = db.query(Product).all()

cafes = db.query(Cafe).all()
if not cafes:
    for name in CAFES:
        db.add(Cafe(name=name))
    db.commit()
    cafes = db.query(Cafe).all()

now = datetime.now(timezone.utc)
created = 0
for day_offset in range(14):
    day = now - timedelta(days=day_offset)
    for _ in range(random.randint(15, 40)):
        sale_time = day.replace(
            hour=random.randint(7, 20), minute=random.randint(0, 59)
        )
        sale = Sale(
            cafe_id=random.choice(cafes).id,
            status="paid",
            created_at=sale_time,
        )
        total = 0
        for product in random.sample(products, random.randint(1, 3)):
            quantity = random.randint(1, 3)
            sale.items.append(
                SaleItem(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                )
            )
            total += product.price * quantity
        sale.total_price = round(total, 2)
        db.add(sale)
        created += 1

db.commit()
db.close()
print(f"Створено {created} демо-чеків за останні 14 днів")
