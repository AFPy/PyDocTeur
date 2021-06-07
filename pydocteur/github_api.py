import logging
import re

import requests
from github import Github, GithubException

from pydocteur.settings import GH_TOKEN
from pydocteur.settings import REPOSITORY_NAME

logger = logging.getLogger("pydocteur")
gh = Github(GH_TOKEN if GH_TOKEN else None)


def get_graphql_api(query: str) -> requests.Response:
    headers = {"Authorization": "Bearer {}".format(GH_TOKEN)}
    resp = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    return resp


def get_pr_from_sha(commit_sha):
    prs_for_commit = gh.search_issues(f"type:pr repo:{REPOSITORY_NAME} sha:{commit_sha}")
    if prs_for_commit.totalCount == 0:
        logger.debug("No PR associated with commit %s", commit_sha, prs_for_commit.totalCount)
        return None
    if prs_for_commit.totalCount != 1:
        logger.error("Should be exactly one PR for this sha: %s, found %s", commit_sha, prs_for_commit.totalCount)
        return None
    return gh.get_repo(REPOSITORY_NAME).get_pull(prs_for_commit[0].number)


def get_pull_request(payload):
    gh_repo = gh.get_repo(REPOSITORY_NAME)
    logger.info("Trying to find PR from %s", payload.get("action", "A payload with: " + ", ".join(payload.keys())))

    head_sha = payload.get("check_suite", {}).get("head_sha")
    if not head_sha:
        head_sha = payload.get("check_run", {}).get("head_sha")
    if head_sha:
        logger.debug(f"Found from head_sha {head_sha}.")
        return get_pr_from_sha(head_sha)

    pr_number = payload.get("pull_request", {}).get("number")
    if pr_number:
        logger.debug(f"Found from pull request number {pr_number}.")
        return gh_repo.get_pull(pr_number)

    issue_number = payload.get("issue", {}).get("number")
    if issue_number:
        logger.debug("Trying to find PR from issue number %s", issue_number)
        try:
            pull_request = gh_repo.get_pull(issue_number)
            logger.debug(f"Found from issue number {issue_number}.")
            return pull_request
        except GithubException:
            pass
    sha = payload.get("before")
    if sha:
        logger.debug(f"Found from `before` sha {sha}.")
        return get_pr_from_sha(sha)

    logger.warning("Unknown payload, (action: %s)", payload.get("action", ""))
    return None


def get_trad_team_members() -> set:
    logger.debug("Getting default reviewers from team members")
    return {
        user.login
        for user in gh.get_organization("afpy").get_team_by_slug("traduction").get_members()
        if user.login != "PyDocTeur"
    }


def has_pr_number(payload) -> bool:
    try:
        payload["pull_request"]["number"]
    except KeyError:
        return False
    else:
        return True


def get_coauthors(pr) -> set:
    co_authored = set()
    compiled_regex = re.compile("(Co-authored-by:.*)")
    for commit in pr.get_commits():
        commit_message = commit.commit.message
        matches = compiled_regex.findall(commit_message)
        if matches:
            for item in matches:
                co_authored.add(item)
    return co_authored


def get_issues_to_close(body):
    return re.findall(r"(?:close[sd]?|fix|fixe[sd]|resolve[sd]?)\s+(#\d+)", body or "", flags=re.IGNORECASE)


def get_commit_message_for_merge(pr):
    logger.info(f"Generating title and message for merge of PR #{pr.number}")
    co_authors = get_coauthors(pr)
    closing_issues = get_issues_to_close(pr.body)

    fixes = "Closes ".join(closing_issues)
    coauthors = "\n".join(co_authors)

    message = "Automerge of PR #{pr_number} by @{author}".format(pr_number=pr.number, author=pr.user.login)
    if fixes:
        message = message + "\n{fixes}".format(fixes=fixes)
    if pr.body:
        message = message + "\n\n{body}".format(body=pr.body)
    if coauthors:
        message = message + "\n\n{coauthors}".format(coauthors=coauthors)
    return message


def rerun_workflow(pr):
    headers = {"Authorization": "Bearer {}".format(GH_TOKEN)}
    url = f"https://api.github.com/repos/python/python-docs-fr/actions/workflows/tests.yml/runs?branch={pr.head.ref}"
    resp = requests.post(url, headers=headers)
    return True if resp.status_code == 201 else False
