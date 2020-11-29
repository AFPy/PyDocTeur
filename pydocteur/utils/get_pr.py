import logging
import os

from github import GithubException


def get_pull_request(gh, payload):
    logging.debug("Getting repository")
    gh_repo = gh.get_repo(os.getenv("REPOSITORY_NAME"))
    logging.info("Trying to find PR number from payload")
    try:
        try:
            pr_number = payload["pull_request"]["number"]
            logging.debug(f"Found PR {pr_number} first try")
        except KeyError:
            try:
                pr_number = payload["check_run"]["pull_requests"][0]["number"]
                logging.debug(f"Found PR {pr_number} second try")
            except KeyError:
                try:
                    pr_number = payload["check_suite"]["pull_requests"][0]["number"]
                    logging.debug(f"Found PR {pr_number} third try")
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
    except:  # noqa
        logging.warning("Unknown payload, returning None")
        logging.debug(payload)
        return None
    return gh_repo.get_pull(pr_number)
