import logging

import requests
from requests.auth import HTTPBasicAuth
from github import GithubException
from github import Github

from pydocteur.settings import GH_TOKEN
from pydocteur.settings import GH_USERNAME
from pydocteur.settings import REPOSITORY_NAME


gh = Github(GH_TOKEN)


def get_rest_api(url: str) -> requests.Response:
    resp = requests.get(url, auth=HTTPBasicAuth(GH_USERNAME, GH_TOKEN))
    return resp


def get_graphql_api(query: str) -> requests.Response:
    headers = {"Authorization": "Bearer {}".format(GH_TOKEN)}
    resp = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    return resp


def get_pull_request(payload):
    logging.debug("Getting repository")
    gh_repo = gh.get_repo(REPOSITORY_NAME)
    logging.info("Trying to find PR number from payload")

    is_run = payload.get("check_run", False)
    is_suite = payload.get("check_suite", False)

    if is_run or is_suite:
        logging.info("Payload is from checks, ignoring")
        return None

    try:
        try:
            pr_number = payload["pull_request"]["number"]
            logging.debug(f"Found PR {pr_number} first try")
        except KeyError:
            issue_number = payload["issue"]["number"]
            logging.debug(f"Found issue {issue_number} from payload")
            try:
                repo = gh_repo.get_pull(issue_number)
                logging.info(f"Found PR #{repo.number}")
                return repo
            except GithubException:
                logging.debug(f"Found issue {issue_number}, returning None")
                return None
    except Exception:  # noqa
        logging.warning("Unknown payload, returning None")
        logging.debug(payload)
        return None
    return gh_repo.get_pull(pr_number)


def get_trad_team_members():
    logging.debug("Getting default reviewers from team members")
    return [user.login for user in gh.get_organization("afpy").get_team_by_slug("traduction").get_members()]


def has_pr_number(payload) -> bool:
    try:
        payload["pull_request"]["number"]
    except KeyError:
        return False
    else:
        return True
