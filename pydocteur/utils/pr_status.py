import requests


def get_checks_statuses_conclusions(pr):
    commits_sha = [commit.sha for commit in pr.get_commits()]
    last_sha = commits_sha[-1]
    resp = requests.get(f"https://api.github.com/repos/pydocteur/fake-docs/commits/{last_sha}/check-runs")
    runs = resp.json()["check_runs"]
    statuses = [run["status"] for run in runs]
    conclusions = [run["conclusion"] for run in runs]
    are_all_checks_done = all(status == "completed" for status in statuses)
    if are_all_checks_done:
        is_ci_success = all(conclusion == "success" for conclusion in conclusions)
    else:
        is_ci_success = False
    return is_ci_success


def are_labels_set(pr):
    pr_labels = pr.get_labels()
    label_names = [label.name for label in pr_labels]
    is_automerge_set = False
    is_donotmerge_set = False
    if "🤖 automerge" in label_names:
        is_automerge_set = True
    if "DO NOT MERGE" in label_names:
        is_donotmerge_set = True
    return is_automerge_set, is_donotmerge_set


def is_pr_approved(pr):
    # TODO: Maybe finer getting of approvals for better control, maybe all reviews don't need to be ok, just one
    pr_reviews = pr.get_reviews()
    is_approved = all(review.state == "APPROVED" for review in pr_reviews)
    return is_approved
