import re

from github import Commit
from github import File
from github import PullRequest

from pydocteur.settings import VERSION

BODY = """

```suggestion
{new_line}
```

---
<details>
  <summary>Disclaimer</summary>

Je suis un robot fait par l'équipe de [l'AFPy et de Traduction](https://github.com/AFPy/PyDocTeur/graphs/contributors)
sur leur temps libre. Je risque de dire des bétises. Ne me blâmez pas, blamez les développeurs.

[Code source](https://github.com/afpy/pydocteur)

I'm a bot made by the [Translation and AFPy teams](https://github.com/AFPy/PyDocTeur/graphs/contributors) on their free
time. I might say or do dumb things sometimes. Don't blame me, blame the developer !

[Source code](https://github.com/afpy/pydocteur)

`PyDocTeur {version}`

</details>
"""


def find_extraneous_nb_spaces(pr: PullRequest, line: str, last_commit: Commit, file: File, index: int):
    for error_match in re.finditer(r"\xa0(?![?!;:])", line):
        error_start, error_end = error_match.span()
        line = line[:error_start] + " " + line[error_end:]
        body = BODY.format(new_line=line, version=VERSION)
        pr.create_review_comment(
            "Il y a un espace insécable en trop ici :\n\n" + body, last_commit, file.filename, index
        )


def find_missing_nb_spaces(pr: PullRequest, line: str, last_commit: Commit, file: File, index: int):
    for error_match in re.finditer(r" [?!;:]", line):
        error_start, error_end = error_match.span()
        line = line[:error_start] + "\xa0" + line[error_start + 1 :]  # noqa
        body = BODY.format(new_line=line, version=VERSION)
        pr.create_review_comment("Il manque un espace insécable ici :\n\n" + body, last_commit, file.filename, index)


def review_pr(pr: PullRequest):
    last_commit = [commit for commit in pr.get_commits()][-1]

    positions_to_ignore = [comment.position for comment in pr.get_review_comments()]

    for file in pr.get_files():
        patch = file.patch
        for index, line in enumerate(patch.split("\n")):
            if not line.startswith("+"):
                # Line isn't a modification
                continue
            if index in positions_to_ignore:
                # Already commented, don't comment again for now
                continue
            if line.startswith('"'):
                # Ignore line as it is a meta line
                continue

            line = line[1:]

            if line.startswith("msgid"):
                body = BODY.format(new_line=line, version=VERSION)
                pr.create_review_comment(
                    "Merci de ne pas modifier les lignes `msgid`.\n"
                    "Si tu a trouvé une erreur dans la documentation originale, "
                    "fait une pull request dans CPython.\n\n" + body,
                    last_commit,
                    file.filename,
                    index,
                )

            find_extraneous_nb_spaces(pr, line, last_commit, file, index)
            find_missing_nb_spaces(pr, line, last_commit, file, index)
