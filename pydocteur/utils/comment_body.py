import json
import logging
import os
from functools import lru_cache

COMMENT_BODIES_FILEPATH = os.path.join(os.path.dirname(__file__), "../../comment_bodies.json")


@lru_cache()
def get_comment_bodies(state):
    logging.debug(f"Getting comment bodies for {state}")
    with open(COMMENT_BODIES_FILEPATH, "r") as handle:
        bodies = json.load(handle).get(state)
    return bodies
