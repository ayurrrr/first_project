import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (format_amount, format_rub, parse_amount,  # noqa: E402
                   parse_start_amount, plain_number)


@pytest.mark.parametrize(
    "text, expected",
    [("100", 100.0), ("100,5", 100.5), ("  7.25 ", 7.25), ("0", 0.0)],
)
def test_parse_amount_ok(text, expected):
    assert parse_amount(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "nan", "inf", "-inf", "-5", "1,2,3"])
def test_parse_amount_bad(text):
    with pytest.raises(ValueError):
        parse_amount(text)


def test_format_amount():
    assert format_amount(1.234567891, "BTC") == "1.234568"
    assert format_amount(1.234567891, "ETH") == "1.234568"
    assert format_amount(1.234567891, "USD") == "1.23"
    assert format_amount(1.234567891, "RUB") == "1.23"


def test_format_rub():
    assert format_rub(12345.6) == "12 345.60 ₽"
    assert format_rub(0) == "0.00 ₽"
    assert format_rub(-1500) == "-1 500.00 ₽"
    assert format_rub(1234567.891) == "1 234 567.89 ₽"


@pytest.mark.parametrize(
    "text, expected",
    [("100000", 100000.0), ("2500,5", 2500.5), (" 1 ", 1.0), ("1000000000000", 1e12)],
)
def test_parse_start_amount_ok(text, expected):
    assert parse_start_amount(text) == expected


@pytest.mark.parametrize("text", ["0", "-100", "abc", "", "nan", "inf", "1000000000001", "1e20"])
def test_parse_start_amount_bad(text):
    with pytest.raises(ValueError):
        parse_start_amount(text)


@pytest.mark.parametrize(
    "value, expected",
    [(100000.0, "100000"), (2500.5, "2500.5"), (0.0, "0"), (1e12, "1000000000000"), (0.25, "0.25")],
)
def test_plain_number(value, expected):
    assert plain_number(value) == expected
