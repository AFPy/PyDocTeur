import pytest
from github import Github

from pydocteur.github_api import get_coauthors
from pydocteur.github_api import get_issues_to_close


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "pr_number, issues_to_close",
    [
        (1393, ["#1391", "#1392"]),
        (1029, ["#968"]),
        (1423, []),
        (1400, ["#1397", "#1398", "#1399", "#1394", "#1395", "#1396"]),
    ],
)
def test_get_issues_to_close(pr_number, issues_to_close):
    gh = Github()
    res = get_issues_to_close(gh.get_repo("python/python-docs-fr").get_pull(pr_number).body)
    assert set(res) == set(issues_to_close)


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "pr_number, coauthors", [(1478, ["Co-authored-by: Antoine <43954001+awecx@users.noreply.github.com>"]), (1494, [])]
)
def test_get_coauthors(pr_number, coauthors):
    gh = Github()
    assert set(get_coauthors(gh.get_repo("python/python-docs-fr").get_pull(pr_number))) == set(coauthors)
