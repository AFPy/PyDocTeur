import logging
import os

from pydocteur.static import REPOSITORY_NAME
from pydocteur.utils.github_api import get_graphql_api
from pydocteur.utils.github_api import get_rest_api


def get_checks_statuses_conclusions(pr):
    logging.info(f"Checking PR #{pr.number} CI results")
    commits_sha = [commit.sha for commit in pr.get_commits()]
    last_sha = commits_sha[-1]
    logging.debug(f"PR #{pr.number} last sha is {last_sha}")
    logging.info(f"Getting runs for PR #{pr.number}")
    resp = get_rest_api(f"https://api.github.com/repos/{REPOSITORY_NAME}/commits/{last_sha}/check-runs")
    runs = resp.json()["check_runs"]
    if not runs:
        logging.info(f"No runs for PR #{pr.number}.")
        return False
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


def is_first_time_contributor(pr):
    logging.info(f"Checking if PR #{pr.number} is from first time contributor")
    owner, name = os.getenv("REPOSITORY_NAME").split("/")
    query = """
    {
      repository(owner: "%s", name: "%s") {
        pullRequest(number: %s) {
          author {
            login
          }
          authorAssociation
        }
      }
    }
    """ % (
        owner,
        name,
        pr.number,
    )
    resp = get_graphql_api(query)
    results = resp.json()
    association = results["data"]["repository"]["pullRequest"]["authorAssociation"]
    return association == "FIRST_TIME_CONTRIBUTOR"


def is_already_greeted(pr):
    my_comments = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    return any("(state: greetings)" in my_comment for my_comment in my_comments)
