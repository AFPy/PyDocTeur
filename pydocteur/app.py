import json
import logging

from flask import Flask
from flask import jsonify
from flask import request

from pydocteur.actions import comment_about_title
from pydocteur.actions import comment_pr
from pydocteur.actions import maybe_greet_user
from pydocteur.actions import merge_and_thank_contributors
from pydocteur.github_api import get_pull_request
from pydocteur.github_api import has_pr_number
from pydocteur.pr_status import get_pr_state
from pydocteur.pr_status import is_title_ok
from pydocteur.settings import VERSION

application = Flask(__name__)

logger = logging.getLogger("pydocteur")

logger.info("************************************************************")
logger.info(f"****** Starting new instance of PyDocTeur {VERSION} *******")
logger.info("************************************************************")


@application.route("/", methods=["POST", "GET"])
def process_incoming_payload():

    if request.method == "GET":
        return (jsonify({"name": "PyDocTeur", "source": "https://github.com/afpy/pydocteur", "version": VERSION}), 200)

    payload = json.loads(request.data)

    if payload["sender"]["login"] == "PyDocTeur":
        logger.info("Received payload sent from PyDocTeur user, ignoring.")
        return "OK", 200
    # If pull request just got opened
    if "action" not in payload:
        logger.info("Received payload from refs updating, ignoring.")
        return "OK", 200
    if payload["action"] == "opened" and not has_pr_number(payload):
        logger.info("Received payload from opened PR, ignoring.")
        return "OK", 200
    pr = get_pull_request(payload)
    if not pr:
        logger.info("Payload received from checks, issue or unknown, ignoring.")
        return "OK", 200
    if pr.is_merged():
        logger.info(f"PR {pr.number} is merged, ignoring.")
        return "OK", 200
    if pr.closed_at:
        logger.info(f"PR {pr.number} is closed, ignoring.")
        return "OK", 200
    if payload["action"] == "labeled" and payload.get("label", {}).get("name") == "Title needs formatting.":
        logger.info(f"PR {pr.number}: Received from Action PR Title checker, ignoring")
        return "OK", 200
    state = get_pr_state(pr)
    logger.info(f"State of PR #{pr.number} is {state}")

    my_comments = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    if my_comments and f"(state: {state})" in my_comments[-1]:
        logger.info(f"State of PR #{pr.number} hasn't changed, ignoring. (state: {state})")
        return "OK", 200

    if not is_title_ok(pr):
        logger.info(f"Title of PR #{pr.number} is incorrect, sending message")
        comment_about_title(pr)
        return "OK", 200

    state_dict = {
        "automerge_approved_testok": merge_and_thank_contributors,
        # ...
    }
    maybe_greet_user(pr)
    state_dict.get(state, comment_pr)(state=state, pr=pr)

    return "OK", 200
