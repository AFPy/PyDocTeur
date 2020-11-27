import random
import time

from github import PullRequest

from pydocteur.utils.comment_body import get_comment_bodies

END_OF_BODY = """

---
<details>
  <summary>Disclaimer</summary>

I'm a bot made by the [Translation and AFPy teams](https://github.com/AFPy/PyDocTeur/graphs/contributors) on their free
time. I might say or do dumb things sometimes. Don't blame me, blame the developer !

[Source code](https://github.com/afpy/pydocteur)

(state: {state})
</details>
"""


def replace_body_variables(pr: PullRequest, body: str):
    print("Replacing variables")
    author = pr.user.login
    reviewers_login = [review.user.login for review in pr.get_reviews()]
    new_body = body.replace("@$AUTHOR", "@" + author)
    if not reviewers_login:
        reviewers_login = ["JulienPalard", "Seluj78"]
    reviewers = ", @".join(reviewers_login)
    new_body = new_body.replace("@$REVIEWERS", "@" + reviewers)
    return new_body


def comment_pr(pr: PullRequest, state: str):
    print("Getting comment bodies choices")
    bodies = get_comment_bodies(state)
    if not bodies:
        print("No comment for state", state)
        return
    print("Choosing body")
    body = random.choice(bodies)
    # TODO: Add replacement of variables from selected body
    body = replace_body_variables(pr, body)
    pr.create_issue_comment(body + END_OF_BODY.format(state=state))


def merge_and_thank_contributors(pr: PullRequest, state: str):
    bodies = get_comment_bodies(state)
    warnings = bodies["warnings"]
    thanks = bodies["thanks"]

    print("MERGING: Sending warning")
    warning_body = random.choice(warnings)
    warning_body = replace_body_variables(pr, warning_body)
    pr.create_issue_comment(warning_body + END_OF_BODY.format(state=state))

    print("MERGING: Sleeping 1s")
    time.sleep(1)

    print("MERGING: MERGING")
    # TODO: Custom commit message/title with nice infos and saying it's auto merged.
    pr.merge(merge_method="squash", commit_message="")

    print("MERGING: Sending thanks")
    thanks_body = random.choice(thanks)
    thanks_body = replace_body_variables(pr, thanks_body)
    pr.create_issue_comment(thanks_body + END_OF_BODY.format(state=state))
