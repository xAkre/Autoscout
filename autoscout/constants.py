import enum

from selenium.webdriver.common.by import By

IMPLICIT_WAIT_TIME = 3


class URL(enum.StrEnum):
    """Application URLs."""

    LOGIN = "https://info-car.pl/oauth2/login"
    LOGIN_REDIRECT = "https://info-car.pl/new"
    CHECK_FREE_DATES = "https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin"
    CHECK_FREE_DATES_REDIRECT = (
        "https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin/wybor-terminu"
    )
    EXAM_DETAILS = "https://info-car.pl/new/prawo-jazdy/zapisz-sie-na-egzamin-na-prawo-jazdy/szczegoly-egzaminu"


class Selector(enum.Enum):
    """DOM selectors."""

    PPK_EXAM_SELECT = (By.ID, "exam")
    LOGIN_EMAIL_INPUT = (By.ID, "username")
    LOGIN_PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "register-button")
    VOIVODESHIP_SELECT_LABEL = (By.CSS_SELECTOR, 'label[for="province"]')
    WORD_CENTER_SELECT_LABEL = (By.CSS_SELECTOR, 'label[for="organization"]')
    CATEGORY_SELECT_LABEL = (By.CSS_SELECTOR, 'label[for="category-select"]')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')
    PRACTICE_EXAM_TYPE = (By.CSS_SELECTOR, 'input[aria-label="PRACTICE"]')
    REJECT_COOKIES_BUTTON = (By.ID, "cookiescript_reject")
