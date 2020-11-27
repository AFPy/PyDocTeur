import os

from github import Github
from github import GithubException


def get_pull_request(payload):
    gh = Github(os.getenv("GH_TOKEN"))
    gh_repo = gh.get_repo(os.getenv("REPOSITORY_NAME"))
    try:
        try:
            pr_number = payload["pull_request"]["number"]
            print(f"Found first try pr number {pr_number}")
        except KeyError:
            try:
                pr_number = payload["check_run"]["pull_requests"][0]["number"]
                print(f"Found second try pr number {pr_number}")
            except KeyError:
                try:
                    pr_number = payload["check_suite"]["pull_requests"][0]["number"]
                    print(f"Found third try pr number {pr_number}")
                except KeyError:
                    issue_number = payload["issue"]["number"]
                    print(f"Found issue number {issue_number}")
                    try:
                        return gh_repo.get_pull(issue_number)
                    except GithubException:
                        return None
    except:  # noqa
        print(payload)
        return None
    return gh_repo.get_pull(pr_number)
