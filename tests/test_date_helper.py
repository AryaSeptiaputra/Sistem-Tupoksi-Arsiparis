from datetime import datetime

import pytest

from app.utils.date_helper import parse_date, parse_dates


def test_parse_date_reads_form_value():
    assert parse_date("2026-10-20", "Tanggal Surat") == datetime(2026, 10, 20)


@pytest.mark.parametrize("value", [None, ""])
def test_parse_date_keeps_empty_value_empty(value):
    assert parse_date(value, "Tanggal Surat") is None


def test_parse_date_passes_datetime_through():
    value = datetime(2026, 1, 2, 3, 4)
    assert parse_date(value, "Tanggal Surat") is value


def test_parse_date_rejects_other_format_with_label():
    with pytest.raises(ValueError, match="Tanggal Kirim harus berformat YYYY-MM-DD"):
        parse_date("20/10/2026", "Tanggal Kirim")


def test_parse_dates_only_returns_sent_fields():
    labels = {"letter_date": "Tanggal Surat", "sent_date": "Tanggal Kirim"}
    assert parse_dates({"letter_date": "2026-10-20", "number": "1"}, labels) == {
        "letter_date": datetime(2026, 10, 20)
    }
