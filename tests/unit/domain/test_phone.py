import pytest

from app.domain.errors import InvalidPhoneError
from app.domain.value_objects.phone import Phone


def test_brazilian_national_number_is_normalized_to_e164() -> None:
    phone = Phone.parse("(11) 99999-8888")

    assert phone.e164 == "+5511999998888"


def test_foreign_number_with_plus_keeps_its_own_country_instead_of_defaulting_to_brazil() -> None:
    assert Phone.parse("+1 415 555 2671").e164 == "+14155552671"


@pytest.mark.parametrize("garbage", ["", "abc", "123", "+1", "uh, my number is eleven"])
def test_unparseable_or_invalid_number_is_rejected(garbage: str) -> None:
    with pytest.raises(InvalidPhoneError):
        Phone.parse(garbage)
