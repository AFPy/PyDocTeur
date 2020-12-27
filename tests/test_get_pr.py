import pytest

from pydocteur.github_api import get_pull_request_from_checks


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "sha, pr_number",
    [
        ("c8f99382f3393c70b01972de396d52ef5a310f91", 1493),
        ("6d2cdff0b45de327175b8630cbf1fdf3ac59d051", 1478),
        ("7aa2ed8abe819d2628ec8d06a1cd431e874ba16b", 1452),
        ("9c2bfe33df09d245c80afeda3ee7228429a941b0", 1423),
    ],
)
def test_get_pr_from_checks(sha, pr_number):
    assert get_pull_request_from_checks(sha).number == pr_number
