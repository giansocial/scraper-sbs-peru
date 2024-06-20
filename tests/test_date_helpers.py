import pytest
from datetime import date

from src.utils.date_helpers import (
    get_month_name,
    generate_date_range,
    format_sbs_date,
    parse_sbs_date,
    is_business_day,
)


def test_get_month_name_enero():
    assert get_month_name(1) == "Enero"


def test_get_month_name_diciembre():
    assert get_month_name(12) == "Diciembre"


def test_get_month_name_invalido():
    assert get_month_name(0) == ""
    assert get_month_name(13) == ""


def test_rango_una_semana():
    dates = generate_date_range(date(2024, 10, 7), date(2024, 10, 11))
    assert len(dates) == 5
    assert all(d.weekday() < 5 for d in dates)


def test_excluye_fines_de_semana():
    dates = generate_date_range(date(2024, 10, 5), date(2024, 10, 13))
    assert all(d.weekday() < 5 for d in dates)


def test_rango_vacio():
    dates = generate_date_range(date(2024, 10, 12), date(2024, 10, 13))
    assert len(dates) == 0


def test_formato_sbs_date():
    assert format_sbs_date(date(2024, 10, 15)) == "15/10/2024"


def test_parseo_valido():
    assert parse_sbs_date("15/10/2024") == date(2024, 10, 15)


def test_parseo_invalido():
    assert parse_sbs_date("invalid") is None


def test_is_business_day_lunes():
    assert is_business_day(date(2024, 10, 14)) is True


def test_is_business_day_sabado():
    assert is_business_day(date(2024, 10, 12)) is False


def test_is_business_day_domingo():
    assert is_business_day(date(2024, 10, 13)) is False
