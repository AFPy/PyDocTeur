import random

from github import PullRequest

from pydocteur.utils.comment_body import get_comment_bodies
from pydocteur.utils.comment_pr import comment_pr


def do_nothing(pr: PullRequest):
    return


def automerge_donotmerge(pr: PullRequest):
    # TODO: Ping the people who added the labels
    bodies = get_comment_bodies("automerge_donotmerge")

    # Find if last message sent is the same
    comments_list = [comment.body for comment in pr.get_issue_comments()]
    for b in bodies:
        if any(b in item for item in comments_list):
            return
    body = random.choice(bodies)
    comment_pr(pr, body)


def approved_donotmerge(pr: PullRequest):
    # TODO: Ping the people who added the labels and approved
    bodies = get_comment_bodies("approved_donotmerge")
    # Find if last message sent is the same
    comments_list = [comment.body for comment in pr.get_issue_comments()]
    for b in bodies:
        if any(b in item for item in comments_list):
            return
    body = random.choice(bodies)
    comment_pr(pr, body)


def ciok_missing_automerge_and_approval(pr: PullRequest):
    pass


def approved_missing_automerge_and_ci(pr: PullRequest):
    pass


def approved_ciok_missing_automerge(pr: PullRequest):
    pass


def all_good_just_missing_review(pr: PullRequest):
    pass


def merge_when_ci_ok(pr: PullRequest):
    pass


def merge_and_thanks(pr: PullRequest):
    # TODO: Add label and message before doing anything to warn that it is being merged
    pass


def only_automerge(pr: PullRequest):
    pass
