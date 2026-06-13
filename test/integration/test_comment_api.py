import pytest


@pytest.fixture
def issue(client, auth_header):
    headers = auth_header()
    project_id = client.post("/projects", json={"name": "Comments Project"}, headers=headers).get_json()["id"]
    issue_id = client.post(f"/projects/{project_id}/issues", json={"title": "Issue"}, headers=headers).get_json()["id"]
    return headers, project_id, issue_id


def test_create_and_list_comments(client, issue):
    headers, project_id, issue_id = issue
    base = f"/projects/{project_id}/issues/{issue_id}/comments"

    resp = client.post(base, json={"body": "first"}, headers=headers)
    assert resp.status_code == 201

    resp = client.get(base, headers=headers)
    assert len(resp.get_json()) == 1


def test_comment_missing_body(client, issue):
    headers, project_id, issue_id = issue
    base = f"/projects/{project_id}/issues/{issue_id}/comments"

    resp = client.post(base, json={}, headers=headers)
    assert resp.status_code == 400


def test_comment_full_lifecycle(client, issue):
    headers, project_id, issue_id = issue
    base = f"/projects/{project_id}/issues/{issue_id}/comments"

    comment_id = client.post(base, json={"body": "before"}, headers=headers).get_json()["id"]

    resp = client.put(f"{base}/{comment_id}", json={"body": "after"}, headers=headers)
    assert resp.get_json()["body"] == "after"

    resp = client.delete(f"{base}/{comment_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"{base}/{comment_id}", headers=headers)
    assert resp.status_code == 404


def test_comment_wrong_author(client, auth_header):
    headers_a = auth_header(username="alice4", email="alice4@example.com")
    headers_b = auth_header(username="bob4", email="bob4@example.com")

    project_id = client.post("/projects", json={"name": "A's project"}, headers=headers_a).get_json()["id"]
    issue_id = client.post(f"/projects/{project_id}/issues", json={"title": "Issue"}, headers=headers_a).get_json()["id"]

    base = f"/projects/{project_id}/issues/{issue_id}/comments"
    comment_id = client.post(base, json={"body": "by A"}, headers=headers_a).get_json()["id"]

    resp = client.put(f"{base}/{comment_id}", json={"body": "hijacked"}, headers=headers_b)
    assert resp.status_code == 403
