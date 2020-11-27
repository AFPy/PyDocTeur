import json
import os

from dotenv import load_dotenv
from flask import Flask
from flask import request

from pydocteur.utils.get_pr import get_pull_request
from pydocteur.utils.pr_status import are_labels_set
from pydocteur.utils.pr_status import get_checks_statuses_conclusions
from pydocteur.utils.pr_status import is_pr_approved


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

    are_labels_set(pr)
    get_checks_statuses_conclusions(pr)
    is_pr_approved(pr)
    return "OK", 200
