from flask import Flask, request
import json
from github import Github
import os
from dotenv import load_dotenv

load_dotenv()
application = Flask(__name__)

gh = Github(os.getenv("GH_TOKEN"))


@application.route('/', methods=['POST'])
def process_incoming_payload():
    payload = json.loads(request.data)
    try:
        action = payload["action"]
    except KeyError:
        return "OK", 200
    if action == "unlabeled":
        label_name = payload["label"]["name"]
        sender = payload["sender"]["login"]
        pr_number = payload["pull_request"]["number"]
        print(f"Label {label_name} was removed by {sender} on merge request #{pr_number}")
    elif action == "labeled":
        label_name = payload["label"]["name"]
        sender = payload["sender"]["login"]
        pr_number = payload["pull_request"]["number"]
        print(f"Label {label_name} was added by {sender} on merge request #{pr_number}")
    elif action == "submitted":
        pr_number = payload["pull_request"]["number"]
        state = payload["review"]["state"]
        user = payload["review"]["user"]["login"]
        message = payload["review"]["body"]
        print(f"PR #{pr_number} was {state} by {user} with message {message}")
    elif action == "review_requested":
        pr_number = payload["pull_request"]["number"]
        reviewer = payload["requested_reviewer"]["login"]
        requester = payload["sender"]["login"]
        print(f"{requester} requested review from {reviewer} on PR #{pr_number}")
    elif action == "created":
        run_number = payload["check_run"]["id"]
        status = payload["check_run"]["status"]
        print(f"Check run {run_number} started with status {status}")
    elif action == "completed":
        if "check_run" in payload:
            run_number = payload["check_run"]["id"]
            conclusion = payload["check_run"]["conclusion"]
            status = payload["check_run"]["status"]
            print(f"Check run {run_number} completed with status {status} and conclusion {conclusion}")
        elif "check_suite" in payload:
            suite_number = payload["check_suite"]["id"]
            conclusion = payload["check_suite"]["conclusion"]
            status = payload["check_suite"]["status"]
            print(f"Check suite {suite_number} completed with status {status} and conclusion {conclusion}")
        else:
            print(f"Keyerror on {action}: \n\n\n\n----------------------------{request.data}----------------------------\n\n\n\n")
    elif action == "closed":
        pr_number = payload["pull_request"]["number"]
        closer = payload["sender"]["login"]
        print(f"PR #{pr_number} was closed by {closer}")
    elif action == "reopened":
        pr_number = payload["pull_request"]["number"]
        opener = payload["sender"]["login"]
        print(f"PR #{pr_number} was reopened by {opener}")
    elif action == "edited":
        pr_number = payload["pull_request"]["number"]
        user = payload["pull_request"]["user"]["login"]
        print(f"PR #{pr_number} was edited by {user}: {payload['changes']}")
    elif action == "opened":
        pr_number = payload["pull_request"]["number"]
        user = payload["pull_request"]["user"]["login"]
        print(f"PR #{pr_number} was opened by {user}")
    else:
        print(f"Unknown action {action}: \n\n\n\n{request.data}\n\n\n\n")
    return "OK", 200
