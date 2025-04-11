from __future__ import annotations

import collections.abc
import dataclasses
import datetime
import os
import typing

DATE_FORMAT = "%Y-%m-%d"
TYPE_CONVERTERS: dict[type, collections.abc.Callable[[str], typing.Any]] = {
    datetime.date: lambda value: datetime.datetime.strptime(value, DATE_FORMAT).date(),
    bool: lambda value: value == "True",
    int: lambda value: int(value),
}


@dataclasses.dataclass(kw_only=True)
class Config:
    """Configuration for the application."""

    # Credentials
    CREDENTIALS_EMAIL: str
    CREDENTIALS_PASSWORD: str
    CREDENTIALS_FIRST_NAME: str
    CREDENTIALS_LAST_NAME: str
    CREDENTIALS_PESEL: str
    CREDENTIALS_PHONE_NUMBER: str
    CREDENTIALS_PKK_NUMBER: str

    # Exam options
    WORD_VOIVODESHIP: str
    WORD_CENTER: str
    WORD_CATEGORY: str

    # Application options
    DATE_TO: datetime.date
    CONFIRM: bool

    @classmethod
    def from_env(cls) -> typing.Self:
        """Load the configuration from the environment variables."""
        type_hints = typing.get_type_hints(cls)
        config = {}

        for field in dataclasses.fields(cls):
            value = os.getenv(field.name)

            if value is None:
                raise ValueError(f"Environment variable {field.name} is not set.")

            type_ = type_hints[field.name]

            if type_ is str:
                config[field.name] = value
            elif type_ in TYPE_CONVERTERS:
                config[field.name] = TYPE_CONVERTERS[type_](value)
            else:
                raise ValueError(f"Unsupported type: {type_}")

        return cls(**config)  # type: ignore[arg-type]
