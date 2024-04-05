import pytest
from datetime import date

from src.utils.date_helpers import (
    get_month_name,
    generate_date_range,
    format_sbs_date,
    parse_sbs_date,
    is_business_day,
)


class TestGetMonthName:
    def test_enero(self):
        assert get_month_name(1) == "Enero"

    def test_diciembre(self):
        assert get_month_name(12) == "Diciembre"

    def test_invalido(self):
        assert get_month_name(0) == ""
        assert get_month_name(13) == ""


class TestGenerateDateRange:
    def test_rango_una_semana(self):
        dates = generate_date_range(date(2024, 10, 7), date(2024, 10, 11))
        assert len(dates) == 5
        assert all(d.weekday() < 5 for d in dates)

    def test_excluye_fines_de_semana(self):
        dates = generate_date_range(date(2024, 10, 5), date(2024, 10, 13))
        assert all(d.weekday() < 5 for d in dates)

    def test_rango_vacio(self):
        dates = generate_date_range(date(2024, 10, 12), date(2024, 10, 13))
        assert len(dates) == 0


class TestFormatSBSDate:
    def test_formato(self):
        assert format_sbs_date(date(2024, 10, 15)) == "15/10/2024"


class TestParseSBSDate:
    def test_parseo_valido(self):
        assert parse_sbs_date("15/10/2024") == date(2024, 10, 15)

    def test_parseo_invalido(self):
        assert parse_sbs_date("invalid") is None


class TestIsBusinessDay:
    def test_lunes(self):
        assert is_business_day(date(2024, 10, 14)) is True

    def test_sabado(self):
        assert is_business_day(date(2024, 10, 12)) is False

    def test_domingo(self):
        assert is_business_day(date(2024, 10, 13)) is False
