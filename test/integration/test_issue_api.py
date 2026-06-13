import pytest


@pytest.fixture
def project(client, auth_header):
    headers = auth_header()
    resp = client.post("/projects", json={"name": "Issues Project"}, headers=headers)
    return headers, resp.get_json()["id"]


def test_create_issue_defaults(client, project):
    headers, project_id = project
    resp = client.post(f"/projects/{project_id}/issues", json={"title": "Bug"}, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "todo"
    assert data["priority"] == "medium"


def test_create_issue_invalid_priority(client, project):
    headers, project_id = project
    resp = client.post(f"/projects/{project_id}/issues", json={"title": "Bug", "priority": "urgent"}, headers=headers)
    assert resp.status_code == 400


def test_issue_status_transition_valid(client, project):
    headers, project_id = project
    issue_id = client.post(f"/projects/{project_id}/issues", json={"title": "Bug"}, headers=headers).get_json()["id"]

    resp = client.put(f"/projects/{project_id}/issues/{issue_id}",
                       json={"title": "Bug", "status": "doing"}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "doing"


def test_issue_status_transition_invalid(client, project):
    headers, project_id = project
    issue_id = client.post(f"/projects/{project_id}/issues", json={"title": "Bug"}, headers=headers).get_json()["id"]

    # todo -> done directly should be rejected
    resp = client.put(f"/projects/{project_id}/issues/{issue_id}",
                       json={"title": "Bug", "status": "done"}, headers=headers)
    assert resp.status_code == 409


def test_list_issues_filter_by_status(client, project):
    headers, project_id = project
    client.post(f"/projects/{project_id}/issues", json={"title": "A"}, headers=headers)
    issue_b = client.post(f"/projects/{project_id}/issues", json={"title": "B"}, headers=headers).get_json()["id"]

    client.put(f"/projects/{project_id}/issues/{issue_b}", json={"title": "B", "status": "doing"}, headers=headers)

    resp = client.get(f"/projects/{project_id}/issues?status=todo", headers=headers)
    titles = [i["title"] for i in resp.get_json()]
    assert "A" in titles and "B" not in titles

    resp = client.get(f"/projects/{project_id}/issues?status=doing", headers=headers)
    titles = [i["title"] for i in resp.get_json()]
    assert "B" in titles


def test_issue_wrong_owner(client, auth_header):
    headers_a = auth_header(username="alice3", email="alice3@example.com")
    headers_b = auth_header(username="bob3", email="bob3@example.com")

    project_id = client.post("/projects", json={"name": "A's project"}, headers=headers_a).get_json()["id"]
    issue_id = client.post(f"/projects/{project_id}/issues", json={"title": "Secret"}, headers=headers_a).get_json()["id"]

    resp = client.get(f"/projects/{project_id}/issues/{issue_id}", headers=headers_b)
    assert resp.status_code == 403
