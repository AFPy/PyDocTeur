import json

import pytest

from pydocteur.github_api import get_pull_request


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "payload_filename, is_success",
    [
        ("check_suite_completed.json", True),
        ("check_suite_completed2.json", True),
        ("check_suite_completed3.json", True),
        ("check_suite_completed4.json", True),
        ("comment_added.json", True),
        ("comment_created.json", True),
        ("comment_created2.json", True),
        ("labeled.json", True),
        ("labeled2.json", True),
        ("pr_unassigned.json", True),
        ("pydocteur_sender.json", True),
        ("refs_update.json", False),
        ("refs_update2.json", False),
        ("refs_update3.json", False),
        ("review_edited.json", True),
        ("review_edited2.json", True),
        ("review_requested.json", True),
        ("review_submitted.json", True),
        ("review_submitted2.json", True),
        ("synchronize.json", True),
        ("unlabeled.json", True),
        ("unlabeled2.json", True),
    ],
)
def test_get_issues_to_close(payload_filename, is_success):
    with open("tests/payloads/" + payload_filename) as handle:
        payload = json.load(handle)
    if get_pull_request(payload):
        pr_or_not = True
    else:
        pr_or_not = False
    assert pr_or_not == is_success
