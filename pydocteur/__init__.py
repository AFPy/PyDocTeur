import json
import os
from functools import partial

from dotenv import load_dotenv
from flask import Flask
from flask import request

from pydocteur.utils.get_pr import get_pull_request
from pydocteur.utils.pr_status import are_labels_set
from pydocteur.utils.pr_status import get_checks_statuses_conclusions
from pydocteur.utils.pr_status import is_pr_approved
from pydocteur.utils.state_actions import comment_pr


load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

application = Flask(__name__)


# Could this dict be auto-generated?
STATE_NAMES = {
    (0, 0, 1, 0): "ciok_missing_automerge_and_approval",
    (0, 1, 0, 0): "approved_missing_automerge_and_ci",
    (0, 1, 0, 1): "approved_donotmerge",
    (0, 1, 1, 0): "approved_ciok_missing_automerge",
    (0, 1, 1, 1): "approved_donotmerge",
    (1, 0, 0, 0): "only_automerge",
    (1, 0, 0, 1): "automerge_donotmerge",
    (1, 0, 1, 0): "all_good_just_missing_review",
    (1, 0, 1, 1): "automerge_donotmerge",
    (1, 1, 0, 0): "merge_when_ci_ok",
    (1, 1, 0, 1): "automerge_donotmerge",
    (1, 1, 1, 0): "merge_and_thanks",
    (1, 1, 1, 1): "automerge_donotmerge",
}


@application.route("/", methods=["POST"])
def process_incoming_payload():
    payload = json.loads(request.data)
    if payload["sender"]["login"] == "PyDocTeur":
        return "OK", 200
    pr = get_pull_request(payload)
    if not pr:
        return "OK", 200

    is_automerge_set, is_donotmerge_set = are_labels_set(pr)
    is_ci_success = get_checks_statuses_conclusions(pr)
    is_approved = is_pr_approved(pr)
    state = (is_automerge_set, is_approved, is_ci_success, is_donotmerge_set)
    last_comment = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    current_state = STATE_NAMES[state]
    if current_state in last_comment:
        print("State has not changed, ignoring event.")
        return
    big_dict = {
        # automerge
        # |   approved
        # |   |  ci ok
        # /   /  /  donotmerge
        (0, 0, 1, 0): comment_pr,
        (0, 1, 0, 0): comment_pr,
        (0, 1, 0, 1): comment_pr,
        (0, 1, 1, 0): comment_pr,
        (0, 1, 1, 1): comment_pr,
        (1, 0, 0, 0): comment_pr,
        (1, 0, 0, 1): comment_pr,
        (1, 0, 1, 0): comment_pr,
        (1, 0, 1, 1): comment_pr,
        (1, 1, 0, 0): comment_pr,
        (1, 1, 0, 1): comment_pr,
        (1, 1, 1, 0): comment_pr,
        (1, 1, 1, 1): comment_pr,
    }
    big_dict.get(state, lambda **kwargs: None)(state_name=current_state, pr=pr)
    return "OK", 200
