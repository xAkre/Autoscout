from __future__ import annotations

import contextlib
import json
import logging
import time
import typing

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from autoscout import constants
from autoscout.constants import URL, Selector

if typing.TYPE_CHECKING:
    from autoscout.config import Config


class Autoscout:
    """Autoscout application."""

    driver: webdriver.Chrome

    def __init__(self, config: Config) -> None:
        """Initialize the application."""
        self.config = config
        self.started = False
        self.stopped = False
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"Autoscout application initialized with config:\n{json.dumps(self.config.__dict__, indent=4, default=str)}"
        )

    def start(self) -> None:
        """Start the application."""
        if self.started:
            self.logger.info("Restarting...")
        else:
            self.logger.info("Starting the application...")

        self.driver = self._create_driver()
        self.started, self.stopped = True, False
        self.driver.implicitly_wait(constants.IMPLICIT_WAIT_TIME)
        self._login()

        while not self.stopped:
            did_error = False

            try:
                self._check_free_appointments()
            except Exception:
                self.logger.exception("Error occurred when checking free appointments.")
                did_error = True

            if self.stopped:
                break

            if did_error:
                self.driver.quit()
                self.start()
                return

            self.logger.info("Sleeping for 10 seconds...")
            time.sleep(10)

        self.logger.info("Application stopped.")

    def stop(self) -> None:
        """Stop the application."""
        self.logger.info("Stopping the application...")
        self.started, self.stopped = False, True
        self.driver.quit()

    def _create_driver(self) -> webdriver.Chrome:
        """Create a driver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", value=True)
        return webdriver.Chrome(options=options)

    def _login(self) -> None:
        """Login to the application."""
        self.logger.info("Logging in to the application...")
        self.driver.get(URL.LOGIN)
        self._input(self.config.CREDENTIALS_EMAIL, Selector.LOGIN_EMAIL_INPUT)
        self._input(self.config.CREDENTIALS_PASSWORD, Selector.LOGIN_PASSWORD_INPUT)
        self._click(Selector.LOGIN_BUTTON)
        self._wait(EC.url_matches(URL.LOGIN_REDIRECT))
        self.logger.info("Logged in to the application.")

    def _check_free_appointments(self) -> None:
        """Check for free appointments."""
        self.logger.info("Checking for free appointments...")
        self.driver.get(URL.CHECK_FREE_DATES)
        self._reject_cookies()
        self._click(Selector.PPK_EXAM_SELECT)
        self._click(Selector.VOIVODESHIP_SELECT_LABEL)
        self._click((By.ID, self.config.WORD_VOIVODESHIP))
        self._click(Selector.WORD_CENTER_SELECT_LABEL)
        self._click((By.ID, self.config.WORD_CENTER))
        self._click(Selector.CATEGORY_SELECT_LABEL)
        self._click((By.ID, self.config.WORD_CATEGORY))
        self._click(Selector.SUBMIT_BUTTON)
        self._wait(EC.url_matches(URL.CHECK_FREE_DATES_REDIRECT))
        self._click(Selector.PRACTICE_EXAM_TYPE)
        self.logger.info("No free appointments found.")

    def _reject_cookies(self) -> None:
        """Reject cookies if the button is present."""
        with contextlib.suppress(NoSuchElementException, TimeoutException):
            self._click(Selector.REJECT_COOKIES_BUTTON)

    def _always_tuple(self, selector: Selector | tuple[str, str]) -> tuple[str, str]:
        """Return a tuple from a Selector or a tuple."""
        return selector.value if isinstance(selector, Selector) else selector

    def _input(self, input: str, selector: Selector | tuple[str, str]) -> None:
        """Input text into an element."""
        self.driver.find_element(*self._always_tuple(selector)).send_keys(input)

    def _click(self, selector: Selector | tuple[str, str]) -> None:
        """Click on an element."""
        self._wait(EC.presence_of_element_located(self._always_tuple(selector)))
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(*self._always_tuple(selector)),
        )

    def _wait(self, condition: typing.Any) -> None:
        """Wait for a condition to be met."""
        WebDriverWait(self.driver, constants.IMPLICIT_WAIT_TIME).until(condition)
