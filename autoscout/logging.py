import logging
import os


def configure() -> None:
    """Configure logging for the application."""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/autoscout.log"),
            logging.StreamHandler(),
        ],
    )

    # Suppress Selenium logging
    logging.getLogger("selenium").setLevel(logging.WARNING)
