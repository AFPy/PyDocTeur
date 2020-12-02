from itertools import groupby
import logging
import os

from pydocteur.github_api import get_graphql_api
from pydocteur.github_api import get_rest_api
from pydocteur.settings import REPOSITORY_NAME

logger = logging.getLogger("pydocteur")


def get_checks_statuses_conclusions(pr):
    logger.info(f"Checking PR #{pr.number} CI results")
    commits_sha = [commit.sha for commit in pr.get_commits()]
    last_sha = commits_sha[-1]
    logger.debug(f"PR #{pr.number} last sha is {last_sha}")
    logger.info(f"Getting runs for PR #{pr.number}")
    resp = get_rest_api(f"https://api.github.com/repos/{REPOSITORY_NAME}/commits/{last_sha}/check-runs")
    runs = resp.json()["check_runs"]
    if not runs:
        logger.info(f"No runs for PR #{pr.number}.")
        return False
    statuses = [run["status"] for run in runs]
    conclusions = [run["conclusion"] for run in runs]
    are_all_checks_done = all(status == "completed" for status in statuses)
    if are_all_checks_done:
        logger.info(f"PR #{pr.number} checks are done, checking conclusions")
        is_ci_success = all(conclusion == "success" for conclusion in conclusions)
    else:
        is_ci_success = False
    logger.info(f"PR #{pr.number} CI is_success: {is_ci_success}")
    return is_ci_success


def is_label_set(pr, label: str):
    logger.info(f"Checking if label {label} is set for PR #{pr.number}")
    return label in {label.name for label in pr.get_labels()}


def is_pr_approved(pr):
    logger.info(f"Checking if PR #{pr.number} is approved")
    pr_reviews = pr.get_reviews()
    if pr_reviews.totalCount == 0:
        logger.info(f"No reviews for PR {pr.number}")
        return False

    def sort_reviews_key(review):
        return review.user.login, review.submitted_at

    last_reviews = []
    for author, reviews in groupby(sorted(pr_reviews, key=sort_reviews_key), key=sort_reviews_key):
        last_reviews.append(list(reviews)[-1])
    is_approved = all(review.state == "APPROVED" for review in last_reviews)
    logger.info(f"is_approved for PR #{pr.number} is {is_approved}")
    return is_approved


def is_first_time_contributor(pr):
    logger.info(f"Checking if PR #{pr.number} is from first time contributor")
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


def state_name(**kwargs):
    SIMPLIFICATIONS = {
        "testok": "",
        "approved_testok": "approved",
        "automerge_testok": "automerge",
        "testok_donotmerge": "donotmerge",
        "approved_testok_donotmerge": "donotmerge",
        "automerge_testok_donotmerge": "automerge_donotmerge",
        "automerge_approved_donotmerge": "automerge_donotmerge",
        "automerge_approved_testok_donotmerge": "automerge_donotmerge",
    }
    state = "_".join(key for key, value in kwargs.items() if value)
    return SIMPLIFICATIONS.get(state, state)


def get_pr_state(pr) -> str:
    return state_name(
        automerge=is_label_set(pr, "🤖 automerge"),
        approved=is_pr_approved(pr),
        testok=get_checks_statuses_conclusions(pr),
        donotmerge=is_label_set(pr, "DO NOT MERGE"),
    )
