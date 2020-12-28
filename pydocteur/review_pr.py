import re

from github import File
from github import PullRequest

from pydocteur.actions import replace_body_variables
from pydocteur.settings import VERSION

REVIEW_BODY = """

Hello @$AUTHOR, j'ai trouvé automatiquement quelques changements à faire dans ta PR
Il t'es parfaitement possible de les ignorer car je peux faire des erreurs ! Merci de ta contribution.

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


CHANGE_BODY = """

```suggestion
{new_line}
```
"""


# TODO : Do all changes for a line inside a single suggestion


def find_extraneous_nb_spaces(line: str, file: File, index: int):
    comments = []
    for error_match in re.finditer(r"\xa0(?![?!;:])", line):
        error_start, error_end = error_match.span()
        line = line[:error_start] + " " + line[error_end:]
        body = CHANGE_BODY.format(new_line=line, version=VERSION)

        comments.append(
            {"path": file.filename, "body": "Il y a une espace insécable en trop ici :\n\n" + body, "position": index}
        )
    return comments


def find_missing_nb_spaces(line: str, file: File, index: int):
    comments = []
    for error_match in re.finditer(r" [?!;:]", line):
        error_start, error_end = error_match.span()
        line = line[:error_start] + "\xa0" + line[error_start + 1 :]  # noqa
        body = CHANGE_BODY.format(new_line=line, version=VERSION)

        comments.append(
            {"path": file.filename, "body": "Il manque une espace insécable ici :\n\n" + body, "position": index}
        )
    return comments


def review_pr(pr: PullRequest):
    last_commit = [commit for commit in pr.get_commits()][-1]

    positions_to_ignore = [comment.position for comment in pr.get_review_comments()]

    comments = []

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
                body = CHANGE_BODY.format(new_line=line, version=VERSION)
                comments.append(
                    {
                        "path": file.filename,
                        "body": "Merci de ne pas modifier les lignes `msgid`.\n"
                        "Si tu a trouvé une erreur dans la documentation originale, "
                        "fait une pull request dans CPython.\n\n" + body,
                        "position": index,
                    }
                )
            comments.extend(find_extraneous_nb_spaces(line, file, index))
            comments.extend(find_missing_nb_spaces(line, file, index))
    body = replace_body_variables(pr, REVIEW_BODY.format(version=VERSION))
    pr.create_review(commit=last_commit, body=body, event="REQUEST_CHANGES", comments=comments)
