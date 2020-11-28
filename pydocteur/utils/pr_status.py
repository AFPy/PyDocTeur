import datetime
import logging
import os

import requests
from requests.auth import HTTPBasicAuth


def get_checks_statuses_conclusions(pr):
    logging.info(f"Checking PR #{pr.number} CI results")
    commits_sha = [commit.sha for commit in pr.get_commits()]
    last_sha = commits_sha[-1]
    logging.debug(f"PR #{pr.number} last sha is {last_sha}")
    resp = requests.get(
        f"https://api.github.com/repos/pydocteur/fake-docs/commits/{last_sha}/check-runs",
        auth=HTTPBasicAuth(os.getenv("GH_USERNAME"), os.getenv("GH_TOKEN")),
    )
    if resp.status_code == 403:
        reset_ts = resp.headers.get("X-Ratelimit-Reset")
        logging.error(f"Rate limit reached, waiting until {reset_ts}")
        while datetime.datetime.utcnow().timestamp() < int(reset_ts):
            continue
    runs = resp.json()["check_runs"]
    statuses = [run["status"] for run in runs if run["name"] != "check-title"]
    conclusions = [run["conclusion"] for run in runs if run["name"] != "check-title"]
    are_all_checks_done = all(status == "completed" for status in statuses)
    if are_all_checks_done:
        logging.info(f"PR #{pr.number} checks are done, checking conclusions")
        is_ci_success = all(conclusion == "success" for conclusion in conclusions)
    else:
        is_ci_success = False
    logging.info(f"PR #{pr.number} CI is_success: {is_ci_success}")
    return is_ci_success


def is_label_set(pr, label: str):
    logging.info(f"Checking if label {label} is set for PR #{pr.number}")
    return label in {label.name for label in pr.get_labels()}


def is_pr_approved(pr):
    logging.info(f"Checking if PR #{pr.number} is approved")
    pr_reviews = pr.get_reviews()
    if pr_reviews.totalCount == 0:
        logging.info(f"No reviews for PR {pr.number}")
        return False
    is_approved = any(review.state == "APPROVED" for review in pr_reviews)
    logging.info(f"is_approved for PR #{pr.number} is {is_approved}")
    return is_approved
