class DomainError(Exception):
    """Base class for domain errors. Only the API layer maps these to HTTP."""


class InvalidPhoneError(DomainError):
    """The phone number could not be parsed or is not a valid number."""


class InvalidPatientError(DomainError):
    """Patient data failed validation (blank name, implausible birth date)."""


class PhoneAlreadyRegisteredError(DomainError):
    """A patient with this phone number already exists."""


class EmailAlreadyRegisteredError(DomainError):
    """A patient with this email already exists."""
