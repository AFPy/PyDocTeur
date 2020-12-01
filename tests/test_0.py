import pytest

from pydocteur.github_api import get_rest_api


@pytest.mark.vcr()
def test_get_rest_api():
    resp = get_rest_api("https://api.github.com/repos/afpy/pydocteur")
    data = resp.json()
    assert data["name"] == "PyDocTeur"
