def test_create_project_requires_auth(client):
    resp = client.post("/projects", json={"name": "No Auth"})
    assert resp.status_code == 401


def test_create_and_list_projects(client, auth_header):
    headers = auth_header()

    resp = client.post("/projects", json={"name": "Project A", "description": "first"}, headers=headers)
    assert resp.status_code == 201

    resp = client.get("/projects", headers=headers)
    names = [p["name"] for p in resp.get_json()]
    assert "Project A" in names


def test_project_full_lifecycle(client, auth_header):
    headers = auth_header()

    resp = client.post("/projects", json={"name": "Lifecycle", "description": "before"}, headers=headers)
    project_id = resp.get_json()["id"]

    resp = client.get(f"/projects/{project_id}", headers=headers)
    assert resp.get_json()["name"] == "Lifecycle"

    resp = client.put(f"/projects/{project_id}", json={"name": "Renamed", "description": "after"}, headers=headers)
    assert resp.get_json()["name"] == "Renamed"

    resp = client.delete(f"/projects/{project_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/projects/{project_id}", headers=headers)
    assert resp.status_code == 404


def test_project_wrong_owner(client, auth_header):
    headers_a = auth_header(username="alice2", email="alice2@example.com")
    headers_b = auth_header(username="bob2", email="bob2@example.com")

    resp = client.post("/projects", json={"name": "Owned by A"}, headers=headers_a)
    project_id = resp.get_json()["id"]

    resp = client.get(f"/projects/{project_id}", headers=headers_b)
    assert resp.status_code == 403
