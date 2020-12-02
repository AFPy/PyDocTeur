import logging
import os
from itertools import groupby

from pydocteur.github_api import get_graphql_api

logger = logging.getLogger("pydocteur")


def is_pr_tests_passed(pr):
    logger.info(f"Checking PR #{pr.number} CI results")
    last_commit = [commit for commit in pr.get_commits()][-1]
    check_suites = last_commit.get_check_suites()
    statuses = [suite.status for suite in check_suites]
    conclusions = [suite.conclusion for suite in check_suites]
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
    pr_reviews = [review for review in pr.get_reviews() if review.state != "COMMENTED"]
    if not pr_reviews:
        logger.info(f"No reviews for PR {pr.number}")
        return False

    def sort_reviews_key(review):
        return review.user.login, review.submitted_at

    last_reviews = []
    for _, reviews in groupby(sorted(pr_reviews, key=sort_reviews_key), key=lambda review: review.user.login):
        last_reviews.append(list(reviews)[-1])
    is_approved = all(review.state == "APPROVED" for review in last_reviews)
    logger.info(
        "is_pr_approved(%s): %s (%s)",
        pr.number,
        is_approved,
        ", ".join(f"{review.user.login} has {review.state}" for review in last_reviews),
    )
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
        testok=is_pr_tests_passed(pr),
        donotmerge=is_label_set(pr, "DO NOT MERGE"),
    )
