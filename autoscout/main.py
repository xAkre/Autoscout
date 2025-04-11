import logging

import dotenv

from autoscout import log
from autoscout.application import Autoscout
from autoscout.config import Config


def main() -> None:
    """Entrypoint for the application."""
    log.configure()
    dotenv.load_dotenv()

    logger = logging.getLogger(__name__)

    config = Config.from_env()
    autoscout = Autoscout(config)

    try:
        autoscout.start()
    except Exception:
        logger.exception("An error occurred. Stopping the application.")
    finally:
        if autoscout.started and not autoscout.stopped:
            autoscout.stop()


if __name__ == "__main__":
    main()
