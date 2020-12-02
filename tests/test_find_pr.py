import pytest
from pydocteur.github_api import get_pull_request


@pytest.mark.vcr()
def test_get_pr_from_check_run():
    payload = {
        "action": "completed",
        "check_run": {
            "id": 1487327954,
            "node_id": "MDg6Q2hlY2tSdW4xNDg3MzI3OTU0",
            "head_sha": "390a392633a4692ee96ebd8d122cfdcd602224e0",
            "external_id": "d133e080-687a-5f71-4d25-419e05f66c84",
            "url": "https://api.github.com/repos/python/python-docs-fr/check-runs/1487327954",
            "html_url": "https://github.com/python/python-docs-fr/runs/1487327954",
            "details_url": "https://github.com/python/python-docs-fr/runs/1487327954",
            "status": "completed",
            "conclusion": "success",
            "started_at": "2020-12-02T16:00:51Z",
            "completed_at": "2020-12-02T16:05:22Z",
            "output": {
                "annotations_count": 0,
            },
        },
    }
    pr = get_pull_request(payload)
    assert pr.number == 1461
