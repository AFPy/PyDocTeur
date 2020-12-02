from pathlib import Path
import os
import logging.config
import yaml

from dotenv import load_dotenv

DEFAULT_LOGGING_CONFIG = """
---

version: 1
disable_existing_loggers: false
handlers:
  stderr:
    class: logging.StreamHandler
    stream: ext://sys.stderr
    level: DEBUG
loggers:
  pydocteur:
    level: DEBUG
    handlers: [stderr]
  urllib3:
    level: INFO
    handlers: [stderr]
  reqests:
    level: INFO
    handlers: [stderr]
  github:
    level: INFO
    handlers: [stderr]
"""

load_dotenv()

REQUIRED_ENV_VARS = ["GH_TOKEN", "REPOSITORY_NAME", "GH_USERNAME"]

for var in REQUIRED_ENV_VARS:
    if var not in os.environ:
        raise EnvironmentError(f"Missing {var} in environment")

GH_USERNAME = os.getenv("GH_USERNAME")
REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")
GH_TOKEN = os.getenv("GH_TOKEN")

VERSION = (Path(__file__).parent.parent / "VERSION").read_text().strip()

logging.config.dictConfig(
    yaml.load(
        Path(os.environ["LOGGING"]).read_text() if "LOGGING" in os.environ else DEFAULT_LOGGING_CONFIG,
        Loader=yaml.SafeLoader,
    )
)
