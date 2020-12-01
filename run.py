from pydocteur import application
from pydocteur.logging import setup_logging


if __name__ == "__main__":
    setup_logging()
    application.run(debug=True, threaded=False)
