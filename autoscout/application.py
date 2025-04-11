from __future__ import annotations

import logging
import typing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from autoscout import constants
from autoscout.constants import ID, URL

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
        self._login()

    def _input(self, input: str, selector: str, by: By = By.ID) -> None:
        """Input text into an element."""
        self.driver.find_element(by, selector).send_keys(input)

    def _click(self, selector: str, by: By = By.ID) -> None:
        """Click on an element."""
        self.driver.find_element(by, selector).click()

    def _wait(self, condition: typing.Any) -> None:
        """Wait for a condition to be met."""
        WebDriverWait(self.driver, constants.IMPLICIT_WAIT_TIME).until(condition)

    def _login(self) -> None:
        """Login to the application."""
        self.logger.info("Logging in to the application...")
        self.driver.get(URL.LOGIN)
        self._input(self.config.CREDENTIALS_EMAIL, ID.LOGIN_EMAIL_INPUT)
        self._input(self.config.CREDENTIALS_PASSWORD, ID.LOGIN_PASSWORD_INPUT)
        self._click(ID.LOGIN_BUTTON)
        self._wait(EC.url_matches(URL.LOGIN_REDIRECT))
        self.logger.info("Logged in to the application.")

    def stop(self) -> None:
        """Stop the application."""
        self.started, self.stopped = False, True
        self.logger.info("Stopping the application...")
        self.driver.quit()
        self.logger.info("Application stopped.")
