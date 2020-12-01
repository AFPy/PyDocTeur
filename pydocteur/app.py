import json
import logging

from flask import Flask
from flask import jsonify
from flask import request

from pydocteur.actions import comment_pr
from pydocteur.actions import maybe_greet_user
from pydocteur.actions import merge_and_thank_contributors
from pydocteur.github_api import get_pull_request, has_pr_number
from pydocteur.settings import VERSION
from pydocteur.pr_status import get_pr_state

application = Flask(__name__)


@application.route("/", methods=["POST", "GET"])
def process_incoming_payload():

    if request.method == "GET":
        return (
            jsonify({"name": "PyDocTeur", "source": "https://github.com/afpy/pydocteur", "version": VERSION}),
            200,
        )

    payload = json.loads(request.data)

    if payload["sender"]["login"] == "PyDocTeur":
        logging.info("Received payload sent from PyDocTeur user, ignoring.")
        return "OK", 200
    # If pull request just got opened
    if "action" not in payload:
        logging.info("Received payload from refs updating, ignoring.")
        return "OK", 200
    if payload["action"] == "opened" and not has_pr_number(payload):
        logging.info("Received payload from opened PR, ignoring.")
        return "OK", 200
    pr = get_pull_request(payload)
    if not pr:
        logging.info("Payload received corresponds to issue or PR not found, ignoring.")
        return "OK", 200
    if pr.is_merged():
        logging.info(f"PR {pr.number} is merged, ignoring.")
        return "OK", 200
    if pr.closed_at:
        logging.info(f"PR {pr.number} is closed, ignoring.")
        return "OK", 200
    if payload["action"] == "labeled" and payload.get("label", {}).get("name") == "Title needs formatting.":
        logging.info(f"PR {pr.number}: Received from Action PR Title checker, ignoring")
        return "OK", 200
    state = get_pr_state(pr)
    logging.info(f"State of PR #{pr.number} is {state}")

    my_comments = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    if my_comments and f"(state: {state})" in my_comments[-1]:
        logging.info(f"State of PR #{pr.number} hasn't changed, ignoring.")
        return "OK", 200

    state_dict = {
        "automerge_approved_testok": merge_and_thank_contributors,
        # ...
    }
    maybe_greet_user(pr)
    state_dict.get(state, comment_pr)(state=state, pr=pr)

    return "OK", 200
