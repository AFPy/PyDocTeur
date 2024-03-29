import json
import logging
import os
import random
import time
from functools import lru_cache

from github import Github
from github import PullRequest

from pydocteur.github_api import get_commit_message_for_merge
from pydocteur.github_api import get_trad_team_members
from pydocteur.pr_status import is_already_greeted
from pydocteur.pr_status import is_first_time_contributor
from pydocteur.settings import GH_TOKEN
from pydocteur.settings import REPOSITORY_NAME
from pydocteur.settings import VERSION

logger = logging.getLogger("pydocteur")

COMMENT_BODIES_FILEPATH = os.path.join(os.path.dirname(__file__), "../comment_bodies.json")


END_OF_BODY = """

---
<details>
  <summary>Disclaimer</summary>

Je suis un robot fait par l'équipe de [l'AFPy et de Traduction](https://github.com/AFPy/PyDocTeur/graphs/contributors)
sur leur temps libre. Je risque de dire des bétises. Ne me blâmez pas, blamez les développeurs.

[Code source](https://github.com/afpy/pydocteur)

I'm a bot made by the [Translation and AFPy teams](https://github.com/AFPy/PyDocTeur/graphs/contributors) on their free
time. I might say or do dumb things sometimes. Don't blame me, blame the developer !

[Source code](https://github.com/afpy/pydocteur)

(state: {state})
`PyDocTeur {version}`

</details>
"""


def replace_body_variables(pr: PullRequest, body: str):
    logger.debug("Replacing variables")
    author = pr.user.login
    reviewers_login = {review.user.login for review in pr.get_reviews()}
    new_body = body.replace("@$AUTHOR", "@" + author)
    if not reviewers_login:
        reviewers_login = get_trad_team_members()
    reviewers_login.discard(author)
    reviewers = ", @".join(reviewers_login)
    new_body = new_body.replace("@$REVIEWERS", "@" + reviewers)
    new_body = new_body.replace("@$MERGEABLE_STATE", pr.mergeable_state)
    return new_body


@lru_cache()
def get_comment_bodies(state):
    logger.debug(f"Getting comment bodies for {state}")
    with open(COMMENT_BODIES_FILEPATH, "r") as handle:
        bodies = json.load(handle).get(state)
    return bodies


def comment_pr(pr: PullRequest, state: str):
    bodies = get_comment_bodies(state)
    if not bodies:
        logger.warning(f"PR #{pr.number}: No comment for state {state}")
        return
    body = random.choice(bodies)
    body = replace_body_variables(pr, body)
    logger.info(f"PR #{pr.number}: Commenting.")
    pr.create_issue_comment(body + END_OF_BODY.format(state=state, version=VERSION))


def merge_and_thank_contributors(pr: PullRequest, state: str):
    gh = Github(GH_TOKEN if GH_TOKEN else None)
    repo = gh.get_repo(REPOSITORY_NAME)
    contributor_usernames = [u.login for u in repo.get_collaborators()]
    reviewer_usernames = [i.user.login for i in pr.get_reviews()]
    if not any(x in reviewer_usernames for x in contributor_usernames):
        logger.info("PR not reviewed by a contributor, not merging.")
        return

    logger.info(f"Testing if PR #{pr.number} can be merged")
    if not pr.mergeable or pr.mergeable_state != "clean":
        logger.warning(f"PR #{pr.number} cannot be merged. mergeable_state={pr.mergeable_state}")
        unmergeable_comments = get_comment_bodies("unmergeable")
        body = random.choice(unmergeable_comments)
        body = replace_body_variables(pr, body)
        pr.create_issue_comment(body + END_OF_BODY.format(state=state, version=VERSION))
        return
    logger.info(f"PR #{pr.number}: About to merge")
    warnings = get_comment_bodies("automerge_approved_testok")
    thanks = get_comment_bodies("automerge_approved_testok-done")

    logger.info(f"PR #{pr.number}: Sending warning before merge")
    warning_body = random.choice(warnings)
    warning_body = replace_body_variables(pr, warning_body)
    pr.create_issue_comment(warning_body + END_OF_BODY.format(state=state, version=VERSION))

    logger.debug(f"PR #{pr.number}: Sleeping one second")
    time.sleep(1)

    message = get_commit_message_for_merge(pr)
    pr.merge(merge_method="squash", commit_message=message)
    logger.info(f"PR #{pr.number}: Merged.")

    logger.info(f"PR #{pr.number}: Sending thanks after merge")
    thanks_body = random.choice(thanks)
    thanks_body = replace_body_variables(pr, thanks_body)
    pr.create_issue_comment(thanks_body + END_OF_BODY.format(state=state, version=VERSION))


def maybe_greet_user(pr: PullRequest):
    if is_first_time_contributor(pr) and not is_already_greeted(pr):
        bodies = get_comment_bodies("greetings")
        body = random.choice(bodies)
        body = replace_body_variables(pr, body)
        logger.info(f"PR #{pr.number}: Greeting {pr.user.login}")
        pr.create_issue_comment(body + END_OF_BODY.format(state="greetings", version=VERSION))


# TODO: Check if changing state for incorrect title may not create a bug where PyDocteur might repeat itself
def comment_about_title(pr: PullRequest):
    bodies = get_comment_bodies("incorrect_title")
    body = random.choice(bodies)
    body = replace_body_variables(pr, body)
    logger.info(f"PR #{pr.number}: Sending incorrect title message")
    pr.create_issue_comment(body + END_OF_BODY.format(state="incorrect_title", version=VERSION))


def comment_about_rerun_workflow(pr: PullRequest):
    bodies = get_comment_bodies("rerun_workflow")
    body = random.choice(bodies)
    body = replace_body_variables(pr, body)
    logger.info(f"PR #{pr.number}: Sending rerun workflow message")
    pr.create_issue_comment(body + END_OF_BODY.format(state="rerun_workflow", version=VERSION))
