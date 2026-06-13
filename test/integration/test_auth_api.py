def test_register_success(client):
    resp = client.post("/auth/register", json={
        "username": "alice", "email": "alice@example.com", "password": "secret123"
    })
    assert resp.status_code == 201
    assert "password" not in resp.get_json()


def test_register_duplicate_username(client):
    payload = {"username": "bob", "email": "bob@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_missing_fields(client):
    resp = client.post("/auth/register", json={"username": "carl"})
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"username": "dave", "email": "dave@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"username": "dave", "password": "secret123"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "erin", "email": "erin@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"username": "erin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/auth/login", json={"username": "frank"})
    assert resp.status_code == 400
