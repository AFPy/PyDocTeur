import os

from github import Github


GH_USERNAME = os.getenv("GH_USERNAME")
REPOSITORY_NAME = os.getenv("REPOSITORY_NAME")
GH_TOKEN = os.getenv("GH_TOKEN")

gh = Github(GH_TOKEN)
