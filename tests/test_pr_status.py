import pytest
from github import Github

from pydocteur.pr_status import is_pr_approved
from pydocteur.pr_status import is_pr_tests_passed


@pytest.mark.vcr()
def test_is_pr_approved():
    gh = Github()
    pr = gh.get_repo("python/python-docs-fr").get_pull(1451)
    assert is_pr_approved(pr)


@pytest.mark.vcr()
def test_is_pr_unapproved():
    gh = Github()
    pr = gh.get_repo("python/python-docs-fr").get_pull(1452)
    assert not is_pr_approved(pr)


@pytest.mark.vcr()
def test_is_pr_tests_failed():
    gh = Github()
    pr = gh.get_repo("python/python-docs-fr").get_pull(1475)
    assert not is_pr_tests_passed(pr)
