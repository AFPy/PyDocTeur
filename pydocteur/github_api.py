import logging

import requests
from requests.auth import HTTPBasicAuth
from github import Github

from pydocteur.settings import GH_TOKEN
from pydocteur.settings import GH_USERNAME
from pydocteur.settings import REPOSITORY_NAME

logger = logging.getLogger("pydocteur")
gh = Github(GH_TOKEN)


def get_rest_api(url: str) -> requests.Response:
    resp = requests.get(url, auth=HTTPBasicAuth(GH_USERNAME, GH_TOKEN))
    return resp


def get_graphql_api(query: str) -> requests.Response:
    headers = {"Authorization": "Bearer {}".format(GH_TOKEN)}
    resp = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    return resp


def get_pull_request_from_check_run(commit_sha):
    prs_for_commit = gh.search_issues(f"type:pr+repo:{REPOSITORY_NAME}+sha:{commit_sha}")
    if prs_for_commit.totalCount != 1:
        logger.error("Should be exactly one PR for this sha: %s, found %s", commit_sha, prs_for_commit.totalCount)
    return prs_for_commit[0]


def get_pull_request(payload):
    gh_repo = gh.get_repo(REPOSITORY_NAME)
    logger.info("Trying to find PR from %s", payload.get("action", "A payload with: " + ", ".join(payload.keys())))

    head_sha = payload.get("check_run", {}).get("head_sha")
    if head_sha:
        return get_pull_request_from_check_run(head_sha)

    pr_number = payload.get("pull_request", {}).get("number")
    if pr_number:
        return gh_repo.get_pull(pr_number)

    issue_number = payload.get("issue", {}).get("number")
    if issue_number:
        return gh_repo.get_pull(issue_number)

    logger.warning("Unknown payload, (action: %s)", payload.get("action", ""))
    return None


def get_trad_team_members() -> set:
    logger.debug("Getting default reviewers from team members")
    return {user.login for user in gh.get_organization("afpy").get_team_by_slug("traduction").get_members()}


def has_pr_number(payload) -> bool:
    try:
        payload["pull_request"]["number"]
    except KeyError:
        return False
    else:
        return True
