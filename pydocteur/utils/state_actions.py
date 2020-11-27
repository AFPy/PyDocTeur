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


def comment_pr(pr: PullRequest, state_name: str):
    print("Getting comment bodies choices")
    bodies = get_comment_bodies(state_name)
    print("Choosing body")
    body = random.choice(bodies)
    # TODO: Add replacement of variables from selected body
    body = replace_body_variables(pr, body)
    pr.create_issue_comment(body + END_OF_BODY.format(last_state=state_name))


def merge_and_thanks(pr: PullRequest, state_name: str):
    # TODO: Add label and message before doing anything to warn that it is being merged
    # Don't forgot to add the state_name in the comment :p
    pass
