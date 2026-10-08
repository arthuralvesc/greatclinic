from dataclasses import dataclass

import phonenumbers

from app.domain.errors import InvalidPhoneError

DEFAULT_REGION = "BR"


@dataclass(frozen=True)
class Phone:
    """A phone number normalized to E.164."""

    e164: str

    @classmethod
    def parse(cls, raw: str) -> "Phone":
        try:
            number = phonenumbers.parse(raw, DEFAULT_REGION)
        except phonenumbers.NumberParseException as exc:
            raise InvalidPhoneError(raw) from exc
        if not phonenumbers.is_valid_number(number):
            raise InvalidPhoneError(raw)
        return cls(phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164))
