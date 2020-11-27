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


def do_nothing(pr: PullRequest, body_request: str):
    return


def comment_pr(pr: PullRequest, body_request: str):
    print("Getting comment bodies choices")
    bodies = get_comment_bodies(body_request)

    # Find if last message sent is the same
    comments_list = [comment.body for comment in pr.get_issue_comments()]
    for b in bodies:
        if any(b in item for item in comments_list):
            print("Last message is the same as the current one. returning")
            return
    print("Choosing body")
    body = random.choice(bodies)

    # TODO: Add replacement of variables from selected body
    body = replace_body_variables(pr, body)
    pr.create_issue_comment(body + END_OF_BODY)


def merge_and_thanks(pr: PullRequest):
    # TODO: Add label and message before doing anything to warn that it is being merged
    pass
