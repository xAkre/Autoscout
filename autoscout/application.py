from __future__ import annotations

import logging
import typing

from selenium import webdriver

from autoscout import constants

if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

    from autoscout.config import Config


class Autoscout:
    """Autoscout application."""

    def __init__(
        self,
        config: Config,
        driver: WebDriver | None = None,
    ) -> None:
        """Initialize the application."""
        if driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(options=options)

        self.config = config
        self.driver = driver
        self.started = False
        self.stopped = False
        self.logger = logging.getLogger(__name__)
        self.logger.info("Autoscout application initialized.")

    def start(self) -> None:
        """Start the application."""
        self.started, self.stopped = True, False
        self.logger.info("Starting the application...")
        self.driver.implicitly_wait(constants.IMPLICIT_WAIT_TIME)

    def stop(self) -> None:
        """Stop the application."""
        self.started, self.stopped = False, True
        self.logger.info("Stopping the application...")
        self.driver.quit()
        self.logger.info("Application stopped.")
