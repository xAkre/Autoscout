from __future__ import annotations

import datetime
import json
import logging
import threading
import time
import typing

import pygame
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
        earliest_date = self._get_earliest_date()

        if earliest_date is None:
            self.logger.info("No appointments available.")
            return

        self.logger.info(f"Earliest date: {earliest_date}")

        if earliest_date > self.config.DATE_TO:
            self.logger.info("Earliest date is after the date to.")
            return

        self._select_earliest_appointment()
        self._fill_in_credentials()

        if self.config.CONFIRM:
            self._confirm()
            counter = 0

            while True:
                if counter * 10 >= constants._30_MINUTES:  # noqa: SLF001
                    self.logger.info("30 minutes have passed. The reservation is no longer valid.")
                    break

                threading.Thread(target=self._play_notification).start()
                self.logger.info(
                    f"Reserved matching appointment {counter * 10} seconds ago. "
                    "Go to the website to pay for the appointment."
                )
                counter += 1
                time.sleep(10)
        else:
            self.logger.info("Skipping confirmation...")

    def _play_notification(self) -> None:
        """Play a notification sound."""
        pygame.mixer.music.load("assets/sound/notification.mp3")
        pygame.mixer.music.play()

    def _get_earliest_date(self) -> datetime.date | None:
        """Get the earliest date available."""
        try:
            self._wait(EC.presence_of_element_located(self._always_tuple(Selector.EARLIEST_DATE_H5)))
            day, month = (
                self.driver.find_element(*self._always_tuple(Selector.EARLIEST_DATE_H5)).text.split(" ")[1].split(".")
            )

            return datetime.date(
                year=datetime.date.today().year,
                month=int(month),
                day=int(day),
            )
        except TimeoutException:
            return None

    def _select_earliest_appointment(self) -> None:
        """Select the earliest appointment."""
        self.logger.info("Selecting the earliest appointment...")
        self._click(Selector.EARLIEST_APPOINTMENT_BUTTON)
        self._click(Selector.CONFIRM_EARLIEST_APPOINTMENT_BUTTON)
        self.logger.info("Earliest appointment selected.")

    def _fill_in_credentials(self) -> None:
        """Fill in the credentials."""
        self.logger.info("Filling in the credentials...")
        self._input(self.config.CREDENTIALS_FIRST_NAME, Selector.CREDENTIALS_FIRST_NAME_INPUT)
        self._input(self.config.CREDENTIALS_LAST_NAME, Selector.CREDENTIALS_LAST_NAME_INPUT)
        self._input(self.config.CREDENTIALS_PESEL, Selector.CREDENTIALS_PESEL_INPUT)
        self._input(self.config.CREDENTIALS_PKK_NUMBER, Selector.CREDENTIALS_PKK_INPUT)
        self._click(Selector.CATEGORY_SELECT_LABEL)
        self._click((By.ID, self.config.WORD_CATEGORY))
        self._input(self.config.CREDENTIALS_EMAIL, Selector.CREDENTIALS_EMAIL_INPUT)
        self._input(self.config.CREDENTIALS_PHONE_NUMBER, Selector.CREDENTIALS_PHONE_INPUT)
        self._click(Selector.CREDENTIALS_ACCEPT_REGULATIONS_CHECKBOX)
        self._click(Selector.CREDENTIALS_NEXT_BUTTON)
        self._wait(EC.url_matches(URL.EXAM_DETAILS))
        self._click(Selector.CREDENTIALS_NEXT_BUTTON)
        self.logger.info("Credentials filled in.")

    def _confirm(self) -> None:
        """Confirm the reservation."""
        self.logger.info("Confirming the reservation...")
        self._click(Selector.CONFIRM_RESERVATION_BUTTON)
        self.logger.info("Reservation confirmed.")

    def _always_tuple(self, selector: Selector | tuple[str, str]) -> tuple[str, str]:
        """Return a tuple from a `Selector` or a `tuple`."""
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
