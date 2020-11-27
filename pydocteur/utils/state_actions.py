import random

from github import PullRequest

from pydocteur.utils.comment_body import get_comment_bodies


END_OF_BODY = """

---
<details>
  <summary>Disclaimer</summary>

I'm a bot made by the [Translation and AFPy teams](https://github.com/AFPy/PyDocTeur/graphs/contributors) on their free
time. I might say or do dumb things sometimes. Don't blame me, blame the developer !

[Source code](https://github.com/afpy/pydocteur)

(last state: {last_state})
</details>
"""


def replace_body_variables(pr: PullRequest, body: str):
    print("Replacing variables")
    author = pr.user.login
    reviewers_login = [review.user.login for review in pr.get_reviews()]
    reviewers = ", @".join(reviewers_login)
    new_body = body.replace("@$AUTHOR", "@" + author)
    new_body = new_body.replace("@$REVIEWERS", "@" + reviewers)
    return new_body


def comment_pr(pr: PullRequest, body_request: str):
    print("Getting comment bodies choices")
    bodies = get_comment_bodies(body_request)

    # Find if last message sent is the same
    last_comment = [comment.body for comment in pr.get_issue_comments() if comment.user.login == "PyDocTeur"]
    if last_comment and body_request in last_comment[-1]:
        print("State has not changed since last time, do not flood.")
        return
    print("Choosing body")
    body = random.choice(bodies)
    # TODO: Add replacement of variables from selected body
    body = replace_body_variables(pr, body)
    pr.create_issue_comment(body + END_OF_BODY.format(last_state=body_request)


def merge_and_thanks(pr: PullRequest):
    # TODO: Add label and message before doing anything to warn that it is being merged
    pass
