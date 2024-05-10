import pytest
import pandas as pd
from datetime import date

from src.transform.cleaner import ExchangeRateCleaner


@pytest.fixture
def cleaner():
    return ExchangeRateCleaner()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "fecha": [date(2024, 10, 1)] * 4 + [date(2024, 10, 1)],
        "entidad": ["BCP", "BBVA", "Interbank", "BCP", "Scotiabank"],
        "compra": [3.78, 3.79, 3.77, 3.78, 3.80],
        "venta": [3.82, 3.83, 3.81, 3.82, 3.84],
        "spread": [0.04, 0.04, 0.04, 0.04, 0.04],
    })


class TestExchangeRateCleaner:
    def test_elimina_duplicados(self, cleaner, sample_df):
        result = cleaner.clean(sample_df)
        assert len(result) == 4

    def test_no_muta_original(self, cleaner, sample_df):
        original_len = len(sample_df)
        cleaner.clean(sample_df)
        assert len(sample_df) == original_len

    def test_elimina_tasas_negativas(self, cleaner):
        df = pd.DataFrame({
            "fecha": [date(2024, 10, 1)] * 2,
            "entidad": ["A", "B"],
            "compra": [3.78, -1.0],
            "venta": [3.82, 3.80],
            "spread": [0.04, 4.80],
        })
        result = cleaner.clean(df)
        assert len(result) == 1

    def test_elimina_venta_menor_que_compra(self, cleaner):
        df = pd.DataFrame({
            "fecha": [date(2024, 10, 1)],
            "entidad": ["X"],
            "compra": [3.85],
            "venta": [3.80],
            "spread": [-0.05],
        })
        result = cleaner.clean(df)
        assert len(result) == 0

    def test_standardize_bank_names(self, cleaner):
        df = pd.DataFrame({
            "entidad": ["B. de Credito del Peru", "Scotiabank Peru", "Unknown Bank"],
        })
        result = cleaner.standardize_bank_names(df)
        assert result["entidad_estandar"].iloc[0] == "BCP"
        assert result["entidad_estandar"].iloc[1] == "Scotiabank"
        assert result["entidad_estandar"].iloc[2] == "Unknown Bank"

    def test_ordena_por_entidad_fecha(self, cleaner, sample_df):
        result = cleaner.clean(sample_df)
        entidades = result["entidad"].tolist()
        assert entidades == sorted(entidades)
