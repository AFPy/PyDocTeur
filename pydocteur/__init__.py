import json
import os
from contextlib import suppress

from dotenv import load_dotenv
from flask import Flask, request
from github import Github

load_dotenv()
application = Flask(__name__)

gh = Github(os.getenv("GH_TOKEN"))


@application.route("/", methods=["POST"])
def process_incoming_payload():
    payload = json.loads(request.data)
    try:
        action = payload["action"]
    except KeyError:
        return "OK", 200

    with suppress(KeyError):
        label_name = payload["label"]["name"]
    with suppress(KeyError):
        sender = payload["sender"]["login"]
    with suppress(KeyError):
        pr_number = payload["pull_request"]["number"]
    with suppress(KeyError):
        user = payload["review"]["user"]["login"]
    with suppress(KeyError):
        run_number = payload["check_run"]["id"]

    if action == "unlabeled":
        print(
            f"Label {label_name} was removed by {sender} on merge request #{pr_number}"
        )
    elif action == "labeled":
        print(f"Label {label_name} was added by {sender} on merge request #{pr_number}")
    elif action == "submitted":
        state = payload["review"]["state"]
        message = payload["review"]["body"]
        print(f"PR #{pr_number} was {state} by {user} with message {message}")
    elif action == "review_requested":
        reviewer = payload["requested_reviewer"]["login"]
        requester = payload["sender"]["login"]
        print(f"{requester} requested review from {reviewer} on PR #{pr_number}")
    elif action == "created":
        status = payload["check_run"]["status"]
        print(f"Check run {run_number} started with status {status}")
    elif action == "completed":
        if "check_run" in payload:
            conclusion = payload["check_run"]["conclusion"]
            status = payload["check_run"]["status"]
            print(
                f"Check run {run_number} completed with status {status} and conclusion {conclusion}"
            )
        elif "check_suite" in payload:
            suite_number = payload["check_suite"]["id"]
            conclusion = payload["check_suite"]["conclusion"]
            status = payload["check_suite"]["status"]
            print(
                f"Check suite {suite_number} completed with status {status} and conclusion {conclusion}"
            )
        else:
            print(
                f"Keyerror on {action}: \n\n\n\n----------------------------{request.data}----------------------------\n\n\n\n"
            )
    elif action == "closed":
        print(f"PR #{pr_number} was closed by {sender}")
    elif action == "reopened":
        print(f"PR #{pr_number} was reopened by {sender}")
    elif action == "edited":
        print(f"PR #{pr_number} was edited by {user}: {payload['changes']}")
    elif action == "opened":
        print(f"PR #{pr_number} was opened by {user}")
    else:
        print(f"Unknown action {action}: \n\n\n\n{request.data}\n\n\n\n")
    return "OK", 200
