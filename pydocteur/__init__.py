import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME", "GH_USERNAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

application = Flask(__name__)
