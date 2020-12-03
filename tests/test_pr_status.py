import pytest
from github import Github

from pydocteur.pr_status import is_pr_approved
from pydocteur.pr_status import is_pr_tests_passed


@pytest.mark.vcr()
@pytest.mark.parametrize("pr_number, approved", [(1451, True), (1490, True), (1452, False)])
def test_is_pr_approved(pr_number, approved):
    gh = Github()
    assert is_pr_approved(gh.get_repo("python/python-docs-fr").get_pull(pr_number)) is approved


@pytest.mark.vcr()
def test_is_pr_tests_failed():
    gh = Github()
    pr = gh.get_repo("python/python-docs-fr").get_pull(1487)
    assert not is_pr_tests_passed(pr)
