import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask import request
from github import Github

from pydocteur.utils.get_pr import get_pull_request
from pydocteur.utils.pr_status import get_checks_statuses_conclusions
from pydocteur.utils.pr_status import is_label_set
from pydocteur.utils.pr_status import is_pr_approved
from pydocteur.utils.state_actions import comment_pr
from pydocteur.utils.state_actions import merge_and_thank_contributors

load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME", "GH_USERNAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

application = Flask(__name__)

gh = Github(os.getenv("GH_TOKEN"))


def state_name(**kwargs):
    SIMPLIFICATIONS = {
        "testok_donotmerge": "donotmerge",
        "approved_testok_donotmerge": "donotmerge",
        "automerge_testok_donotmerge": "automerge_donotmerge",
        "automerge_approved_donotmerge": "automerge_donotmerge",
        "automerge_approved_testok_donotmerge": "automerge_donotmerge",
    }
    state = "_".join(key for key, value in kwargs.items() if value)
    return SIMPLIFICATIONS.get(state, state)


@application.route("/", methods=["POST"])
def process_incoming_payload():
    payload = json.loads(request.data)
    if payload["sender"]["login"] == "PyDocTeur":
        logging.info("Received payload sent from PyDocTeur user, ignoring.")
        return "OK", 200

    # If pull request just got opened
    try:
        if payload["action"] == "opened":
            try:
                payload["pull_request"]["number"]
            except KeyError:
                pass
            else:
                logging.info("Received payload from opened PR, ignoring.")
                return "OK", 200
    except KeyError:
        logging.info("Received payload from refs updating, ignoring.")
        return "OK", 200

    pr = get_pull_request(gh, payload)
    if not pr:
        logging.info("Payload received corresponds to issue or PR not found, ignoring.")
        return "OK", 200

    if pr.is_merged():
        logging.info(f"PR {pr.number} is merged, ignoring.")
        return "OK", 200

    if pr.closed_at:
        logging.info(f"PR {pr.number} is closed, ignoring.")
        return "OK", 200

    try:
        if payload["action"] == "labeled" and payload["label"]["name"] == "Title needs formatting.":
            logging.info(f"PR {pr.number}: Received from Action PR Title checker, ignoring")
            return "OK", 200
    except KeyError:
        pass

    state = state_name(
        automerge=is_label_set(pr, "🤖 automerge"),
        approved=is_pr_approved(pr),
        testok=get_checks_statuses_conclusions(pr),
        donotmerge=is_label_set(pr, "DO NOT MERGE"),
    )
    my_comments = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    if my_comments and f"(state: {state})" in my_comments[-1]:
        logging.info(f"State of PR #{pr.number} hasn't changed, ignoring.")
        return "OK", 200
    state_dict = {
        "automerge_approved_testok": merge_and_thank_contributors,
        # ...
    }
    state_dict.get(state, comment_pr)(state=state, pr=pr)
    return "OK", 200
