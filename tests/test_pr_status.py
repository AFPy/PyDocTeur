import os

import pytest
from github import Github

from pydocteur.pr_status import is_already_greeted
from pydocteur.pr_status import is_first_time_contributor
from pydocteur.pr_status import is_label_set
from pydocteur.pr_status import is_pr_approved
from pydocteur.pr_status import is_pr_tests_passed

REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")


@pytest.mark.vcr()
@pytest.mark.parametrize("pr_number, approved", [(1451, True), (1490, True), (1452, False), (1478, False)])
def test_is_pr_approved(pr_number, approved):
    gh = Github()
    assert is_pr_approved(gh.get_repo(REPOSITORY_NAME).get_pull(pr_number)) is approved


@pytest.mark.vcr()
def test_is_pr_tests_failed():
    gh = Github()
    pr = gh.get_repo("python/python-docs-fr").get_pull(1487)
    assert not is_pr_tests_passed(pr)


@pytest.mark.vcr()
def test_is_pr_tests_success():
    gh = Github()
    pr = gh.get_repo(REPOSITORY_NAME).get_pull(1485)
    assert is_pr_tests_passed(pr)


@pytest.mark.vcr()
def test_is_label_set():
    gh = Github()
    pr = gh.get_repo(REPOSITORY_NAME).get_pull(1485)
    assert is_label_set(pr, "🤖 automerge")
    assert not is_label_set(pr, "DO NOT MERGE")


@pytest.mark.vcr()
@pytest.mark.parametrize("pr_number, is_firsttime", [(13, True), (17, False)])
def test_is_first_time_contributor(pr_number, is_firsttime):
    gh = Github()
    assert is_first_time_contributor(gh.get_repo("pydocteur/fake-docs").get_pull(pr_number)) is is_firsttime


@pytest.mark.vcr()
@pytest.mark.parametrize("pr_number, is_greeted", [(13, True), (17, False)])
def test_is_already_greeted(pr_number, is_greeted):
    gh = Github()
    assert is_already_greeted(gh.get_repo("pydocteur/fake-docs").get_pull(pr_number)) is is_greeted
