from cafe_pos.database import get_db
from cafe_pos.models.user import User, UserRole
from cafe_pos.services.auth_service import hash_password


def register_and_login(client, email, password="Password123"):
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_admin(client, email, password="AdminPass123"):
    db = next(client.app.dependency_overrides[get_db]())
    admin = User(
        email=email, hashed_password=hash_password(password), role=UserRole.admin
    )
    db.add(admin)
    db.commit()
    db.close()
    resp = client.post("/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_anonymous_access_is_rejected(client):
    response = client.get("/user/home")
    assert response.status_code == 401


def test_login_success_and_wrong_password(client):
    client.post(
        "/auth/register", json={"email": "a@test.com", "password": "Password123"}
    )

    ok = client.post(
        "/auth/login", data={"username": "a@test.com", "password": "Password123"}
    )
    assert ok.status_code == 200
    assert "access_token" in ok.json()

    bad = client.post(
        "/auth/login", data={"username": "a@test.com", "password": "wrong"}
    )
    assert bad.status_code == 401


def test_vertical_role_restriction(client):
    headers = register_and_login(client, "user@test.com")
    response = client.get("/admin/home", headers=headers)
    assert response.status_code == 403


def test_horizontal_idor_protection(client):
    headers_a = register_and_login(client, "victim@test.com")
    user_a_id = client.get("/users/1", headers=headers_a).json()["id"]

    headers_b = register_and_login(client, "attacker@test.com")

    response = client.put(
        f"/users/{user_a_id}",
        json={"full_name": "Зламано"},
        headers=headers_b,
    )
    assert response.status_code == 403
