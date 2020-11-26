from flask import Flask, request
import json

application = Flask(__name__)


@application.route('/', methods=['POST'])
def process_incoming_payload():
    payload = json.loads(request.data)
    action = payload["action"]
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
    else:
        print(f"Unknown action {action}: \n\n\n\n{request.data}\n\n\n\n")
    return "OK", 200
