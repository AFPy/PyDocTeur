# PyDocTeur

PyDocTeur is a bot used in python-docs-fr automation


## Configuration

PyDocTeur will use the following environment (and `.env` file) variables:

- `GH_TOKEN` (required): Github access token
- `REPOSITORY_NAME` (required): Github repository name on which the bot should work
- `GH_USERNAME` (required): Bot username on Github.
- `LOGGING` (optional): logging dict-config as a yaml file, see below.


## Github WebHook Configuration

You'll need to setup a github webhook using the `application/json` content type, sending:

- Check suites
- Pull request review comments
- Pull request reviews
- Pull requests
- Pushes
- Issue comments (which in fact also contains pull request comments)


## Logging

PyDocTeur use the `pydocteur` logger, and used libs use the following
loggers: `requests`, `urllib3`, and `github`.

You can personalize how each logger is handled by using a `yaml` file
given in the `LOGGING` environment variable. Here's the default
configuration, so you can bootstrap from it:

```yaml
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
```

## Disclaimer

This bot is heavily inspired by
[miss-iligton](https://github.com/python/miss-islington) made by
[Mariatta](https://github.com/Mariatta) for
[Cpython](https://github.com/python/cpython)

TODO: mypy
