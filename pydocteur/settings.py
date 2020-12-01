import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME", "GH_USERNAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

GH_USERNAME = os.getenv("GH_USERNAME")
REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")
GH_TOKEN = os.getenv("GH_TOKEN")

VERSION = (Path(__file__).parent.parent.parent / "VERSION").read_text().strip()
