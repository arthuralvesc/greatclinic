class DomainError(Exception):
    """Base class for domain errors. Only the API layer maps these to HTTP."""


class InvalidPhoneError(DomainError):
    """The phone number could not be parsed or is not a valid number."""
