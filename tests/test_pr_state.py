import os

import pytest
from github import Github

from pydocteur.pr_status import get_pr_state

REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "pr_number, state",
    [(1490, "automerge_approved_testok"), (1485, "automerge_approved_testok"), (1489, "automerge"), (1487, "")],
)
def test_pr_state(pr_number, state):
    gh = Github()
    assert get_pr_state(gh.get_repo(REPOSITORY_NAME).get_pull(pr_number)) == state
