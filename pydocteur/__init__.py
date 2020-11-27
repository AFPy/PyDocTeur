import json
import os

from dotenv import load_dotenv
from flask import Flask
from flask import request

from pydocteur.utils.get_pr import get_pull_request
from pydocteur.utils.pr_status import are_labels_set
from pydocteur.utils.pr_status import get_checks_statuses_conclusions
from pydocteur.utils.pr_status import is_pr_approved
from pydocteur.utils.state_actions import all_good_just_missing_review
from pydocteur.utils.state_actions import approved_ciok_missing_automerge
from pydocteur.utils.state_actions import approved_donotmerge
from pydocteur.utils.state_actions import approved_missing_automerge_and_ci
from pydocteur.utils.state_actions import automerge_donotmerge
from pydocteur.utils.state_actions import ciok_missing_automerge_and_approval
from pydocteur.utils.state_actions import do_nothing
from pydocteur.utils.state_actions import merge_and_thanks
from pydocteur.utils.state_actions import merge_when_ci_ok
from pydocteur.utils.state_actions import only_automerge


load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

application = Flask(__name__)


@application.route("/", methods=["POST"])
def process_incoming_payload():
    payload = json.loads(request.data)
    pr = get_pull_request(payload)

    is_automerge_set, is_donotmerge_set = are_labels_set(pr)
    is_ci_success = get_checks_statuses_conclusions(pr)
    is_approved = is_pr_approved(pr)
    state = [is_automerge_set, is_approved, is_ci_success, is_donotmerge_set]
    big_dict = {
        # automerge
        #      approved
        #              ci ok
        #                     donotmerge
        [False, False, False, False]: do_nothing,
        [False, False, False, True]: do_nothing,
        [False, False, True, False]: ciok_missing_automerge_and_approval,
        [False, False, True, True]: do_nothing,
        [False, True, False, False]: approved_missing_automerge_and_ci,
        [False, True, False, True]: approved_donotmerge,
        [False, True, True, False]: approved_ciok_missing_automerge,
        [False, True, True, True]: approved_donotmerge,
        [True, False, False, False]: only_automerge,
        [True, False, False, True]: automerge_donotmerge,
        [True, False, True, False]: all_good_just_missing_review,
        [True, False, True, True]: automerge_donotmerge,
        [True, True, False, False]: merge_when_ci_ok,
        [True, True, False, True]: automerge_donotmerge,
        [True, True, True, False]: merge_and_thanks,
        [True, True, True, True]: automerge_donotmerge,
    }
    big_dict[state](pr)
    return "OK", 200
