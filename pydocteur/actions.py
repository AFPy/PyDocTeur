import json
import logging
import os
import random
import time
from functools import lru_cache
from pathlib import Path

from github import PullRequest

from pydocteur.github_api import get_trad_team_members

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


@lru_cache(maxsize=1)
def version():
    return (Path(__file__).parent.parent / "VERSION").read_text()


def replace_body_variables(pr: PullRequest, body: str):
    logging.debug("Replacing variables")
    author = pr.user.login
    reviewers_login = {review.user.login for review in pr.get_reviews()}
    new_body = body.replace("@$AUTHOR", "@" + author)
    if not reviewers_login:
        reviewers_login = get_trad_team_members()
    reviewers = ", @".join(reviewers_login)
    new_body = new_body.replace("@$REVIEWERS", "@" + reviewers)
    return new_body


@lru_cache()
def get_comment_bodies(state):
    logging.debug(f"Getting comment bodies for {state}")
    with open(COMMENT_BODIES_FILEPATH, "r") as handle:
        bodies = json.load(handle).get(state)
    return bodies


def comment_pr(pr: PullRequest, state: str):
    bodies = get_comment_bodies(state)
    if not bodies:
        logging.warning(f"PR #{pr.number}: No comment for state {state}")
        return
    body = random.choice(bodies)
    body = replace_body_variables(pr, body)
    logging.info(f"PR #{pr.number}: Commenting.")
    pr.create_issue_comment(body + END_OF_BODY.format(state=state, version=version()))


def merge_and_thank_contributors(pr: PullRequest, state: str):
    logging.info(f"PR #{pr.number}: About to merge")
    warnings = get_comment_bodies("automerge_approved_testok")
    thanks = get_comment_bodies("automerge_approved_testok-done")

    logging.info(f"PR #{pr.number}: Sending warning before merge")
    warning_body = random.choice(warnings)
    warning_body = replace_body_variables(pr, warning_body)
    pr.create_issue_comment(warning_body + END_OF_BODY.format(state=state, version=version()))

    logging.debug(f"PR #{pr.number}: Sleeping one second")
    time.sleep(1)

    # TODO: Custom commit message/title with nice infos and saying it's auto merged.
    pr.merge(merge_method="squash", commit_message="")
    logging.info(f"PR #{pr.number}: Merged.")

    logging.info(f"PR #{pr.number}: Sending thanks after merge")
    thanks_body = random.choice(thanks)
    thanks_body = replace_body_variables(pr, thanks_body)
    pr.create_issue_comment(thanks_body + END_OF_BODY.format(state=state, version=version()))


def greet_user(pr: PullRequest):
    bodies = get_comment_bodies("greetings")
    body = random.choice(bodies)
    body = replace_body_variables(pr, body)
    logging.info(f"PR #{pr.number}: Greeting {pr.user.login}")
    pr.create_issue_comment(body + END_OF_BODY.format(state="greetings", version=version()))
