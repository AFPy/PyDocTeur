import os

from github import Github


def get_pull_request(payload):
    gh = Github(os.getenv("GH_TOKEN"))
    gh_repo = gh.get_repo(os.getenv("REPOSITORY_NAME"))

    try:
        pr_number = payload["pull_request"]["number"]
        print(f"Found first try pr number {pr_number}")
    except KeyError:
        try:
            pr_number = payload["check_run"]["pull_requests"][0]["number"]
            print(f"Found second try pr number {pr_number}")
        except KeyError:
            pr_number = payload["check_suite"]["pull_requests"][0]["number"]
            print(f"Found third try pr number {pr_number}")
    return gh_repo.get_pull(pr_number)
