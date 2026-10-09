"""Сценарій навантажувального тестування cafe-pos-saas (Locust).

Три типи віртуальних користувачів:
  CashierUser - каса в кав'ярні: дивиться меню і створює чеки (запис у БД).
  OwnerUser   - власник мережі: відкриває аналітику (важкі SELECT з GROUP BY).
  LoginUser   - масові входи: перевірка bcrypt (дорога операція для CPU).

Логін і пароль адміна беруться зі змінних оточення, у коді їх немає:
  LOAD_ADMIN_EMAIL, LOAD_ADMIN_PASSWORD

Запуск (приклад):
  locust -f loadtests/locustfile.py --host http://127.0.0.1:8000
"""

import os
import random

from locust import HttpUser, between, task
from locust.exception import StopUser

ADMIN_EMAIL = os.getenv("LOAD_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("LOAD_ADMIN_PASSWORD", "admin12345")


class CafeBaseUser(HttpUser):
    """Спільна логіка: вхід і підстановка JWT-токена в заголовок."""

    abstract = True

    def login(self):
        with self.client.post(
            "/auth/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            name="POST /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Вхід не вдався: {response.status_code}")
                return False
            token = response.json()["access_token"]
            response.success()
        self.client.headers.update({"Authorization": f"Bearer {token}"})
        return True


class CashierUser(CafeBaseUser):
    """Каса: один раз входить, далі дивиться меню і пробиває чеки."""

    weight = 7
    wait_time = between(1, 3)

    def on_start(self):
        if not self.login():
            raise StopUser()
        # Беремо справжні id товарів і кав'ярень, щоб чеки були коректні.
        products = self.client.get("/products/", name="GET /products/").json()
        cafes = self.client.get("/cafes/", name="GET /cafes/").json()
        self.product_ids = [p["id"] for p in products]
        self.cafe_ids = [c["id"] for c in cafes]
        if not self.product_ids or not self.cafe_ids:
            # Без демо-даних сценарій не має сенсу.
            raise StopUser()

    @task(3)
    def list_products(self):
        self.client.get("/products/", name="GET /products/")

    @task(1)
    def list_cafes(self):
        self.client.get("/cafes/", name="GET /cafes/")

    @task(5)
    def create_sale(self):
        count = random.randint(1, min(3, len(self.product_ids)))
        items = [
            {"product_id": pid, "quantity": random.randint(1, 3)}
            for pid in random.sample(self.product_ids, count)
        ]
        payload = {"cafe_id": random.choice(self.cafe_ids), "items": items}
        self.client.post("/sales/", json=payload, name="POST /sales/")

    @task(1)
    def root(self):
        self.client.get("/", name="GET /")


class OwnerUser(CafeBaseUser):
    """Власник мережі: дивиться аналітику, поки каси пишуть чеки."""

    weight = 2
    wait_time = between(2, 5)

    def on_start(self):
        if not self.login():
            raise StopUser()

    @task(3)
    def summary(self):
        self.client.get("/analytics/summary", name="GET /analytics/summary")

    @task(2)
    def revenue_by_day(self):
        self.client.get(
            "/analytics/revenue-by-day?days=14", name="GET /analytics/revenue-by-day"
        )

    @task(2)
    def top_products(self):
        self.client.get("/analytics/top-products", name="GET /analytics/top-products")

    @task(2)
    def by_cafe(self):
        self.client.get("/analytics/by-cafe", name="GET /analytics/by-cafe")

    @task(1)
    def last_sales(self):
        self.client.get("/sales/?limit=20", name="GET /sales/")


class LoginUser(CafeBaseUser):
    """Постійні входи без роботи після них. Показує ціну bcrypt."""

    weight = 1
    wait_time = between(3, 6)

    @task
    def only_login(self):
        self.login()
