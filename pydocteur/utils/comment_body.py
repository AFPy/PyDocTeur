import json
import os

COMMENT_BODIES_FILEPATH = os.path.join(os.path.dirname(__file__), "../../comment_bodies.json")


def get_comment_bodies(from_where):
    with open(COMMENT_BODIES_FILEPATH, "r") as handle:
        bodies = json.load(handle)[from_where]
    return bodies
