import enum

IMPLICIT_WAIT_TIME = 3


class URL(enum.StrEnum):
    """Application URLs."""

    LOGIN = "https://info-car.pl/oauth2/login"
    LOGIN_REDIRECT = "https://info-car.pl/new"
    CHECK_FREE_DATES = "https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin"
    EXAM_DETAILS = "https://info-car.pl/new/prawo-jazdy/zapisz-sie-na-egzamin-na-prawo-jazdy/szczegoly-egzaminu"
