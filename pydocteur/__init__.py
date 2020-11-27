import json
import os

from dotenv import load_dotenv
from flask import Flask
from flask import request

from pydocteur.utils.get_pr import get_pull_request
from pydocteur.utils.pr_status import are_labels_set
from pydocteur.utils.pr_status import get_checks_statuses_conclusions
from pydocteur.utils.pr_status import is_pr_approved
from pydocteur.utils.state_actions import comment_pr
from pydocteur.utils.state_actions import do_nothing


load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

application = Flask(__name__)


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
    state = [is_automerge_set, is_approved, is_ci_success, is_donotmerge_set]

    state_map = map(int, state)

    state_ints_list = list(state_map)
    str_state = "".join(str(n) for n in state_ints_list)
    big_dict = {
        # automerge
        #      approved
        #              ci ok
        #                     donotmerge
        "0000": [do_nothing, ""],
        "0001": [do_nothing, ""],
        "0010": [comment_pr, "ciok_missing_automerge_and_approval"],
        "0011": [do_nothing, ""],
        "0100": [comment_pr, "approved_missing_automerge_and_ci"],
        "0101": [comment_pr, "approved_donotmerge"],
        "0110": [comment_pr, "approved_ciok_missing_automerge"],
        "0111": [comment_pr, "approved_donotmerge"],
        "1000": [comment_pr, "only_automerge"],
        "1001": [comment_pr, "automerge_donotmerge"],
        "1010": [comment_pr, "all_good_just_missing_review"],
        "1011": [comment_pr, "automerge_donotmerge"],
        "1100": [comment_pr, "merge_when_ci_ok"],
        "1101": [comment_pr, "automerge_donotmerge"],
        "1110": [comment_pr, "merge_and_thanks"],
        "1111": [comment_pr, "automerge_donotmerge"],
    }
    big_dict[str_state][0](pr, big_dict[str_state][1])
    return "OK", 200
