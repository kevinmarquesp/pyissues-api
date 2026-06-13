from domain.entities import Issue, Status


def _make_issue(status: str) -> Issue:
    return Issue(
        id=1, project_id=1, title="Test issue",
        description=None, status=status, priority="medium"
    )


def test_same_status_is_always_allowed():
    issue = _make_issue(Status.TODO.value)
    assert issue.can_transition_to(Status.TODO.value) is True


def test_todo_can_move_to_doing():
    issue = _make_issue(Status.TODO.value)
    assert issue.can_transition_to(Status.DOING.value) is True


def test_todo_cannot_move_to_done_directly():
    issue = _make_issue(Status.TODO.value)
    assert issue.can_transition_to(Status.DONE.value) is False


def test_doing_can_move_to_done_or_back_to_todo():
    issue = _make_issue(Status.DOING.value)
    assert issue.can_transition_to(Status.DONE.value) is True
    assert issue.can_transition_to(Status.TODO.value) is True


def test_done_can_only_move_back_to_doing():
    issue = _make_issue(Status.DONE.value)
    assert issue.can_transition_to(Status.DOING.value) is True
    assert issue.can_transition_to(Status.TODO.value) is False
