import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta

from src.transform.spread_analyzer import SpreadAnalyzer


@pytest.fixture
def analyzer():
    return SpreadAnalyzer()


@pytest.fixture
def daily_data():
    dates = [date(2024, 10, 1) + timedelta(days=i) for i in range(30)]
    records = []
    for d in dates:
        for bank in ["BCP", "BBVA"]:
            base = 3.78 if bank == "BCP" else 3.79
            records.append({
                "fecha": d,
                "entidad": bank,
                "compra": base + np.random.uniform(-0.02, 0.02),
                "venta": base + 0.04 + np.random.uniform(-0.01, 0.01),
                "spread": 0.04,
            })
    return pd.DataFrame(records)


class TestSpreadAnalyzer:
    def test_agrega_spread_pct(self, analyzer, daily_data):
        result = analyzer.analyze(daily_data)
        assert "spread_pct" in result.columns
        assert (result["spread_pct"] > 0).all()

    def test_agrega_medias_moviles(self, analyzer, daily_data):
        result = analyzer.analyze(daily_data)
        assert "spread_ma_5d" in result.columns
        assert "spread_ma_20d" in result.columns

    def test_agrega_volatilidad(self, analyzer, daily_data):
        result = analyzer.analyze(daily_data)
        assert "volatilidad_5d" in result.columns

    def test_no_muta_original(self, analyzer, daily_data):
        original_cols = set(daily_data.columns)
        analyzer.analyze(daily_data)
        assert set(daily_data.columns) == original_cols

    def test_rank_banks(self, analyzer, daily_data):
        ranking = analyzer.rank_banks(daily_data)
        assert "ranking" in ranking.columns
        assert len(ranking) == 2
        assert ranking.iloc[0]["ranking"] == 1

    def test_rank_banks_vacio(self, analyzer):
        ranking = analyzer.rank_banks(pd.DataFrame())
        assert ranking.empty

    def test_detect_spread_anomalies_estable(self, analyzer):
        df = pd.DataFrame({
            "fecha": [date(2024, 10, i) for i in range(1, 11)],
            "entidad": ["BCP"] * 10,
            "compra": [3.78] * 10,
            "venta": [3.82] * 10,
            "spread": [0.04] * 10,
        })
        result = analyzer.detect_spread_anomalies(df)
        assert result["spread_anomaly"].sum() == 0

    def test_detect_spread_anomalies_spike(self, analyzer):
        spreads = [0.04] * 19 + [0.50]
        df = pd.DataFrame({
            "fecha": [date(2024, 10, 1) + timedelta(days=i) for i in range(20)],
            "entidad": ["BCP"] * 20,
            "compra": [3.78] * 20,
            "venta": [3.82] * 19 + [4.28],
            "spread": spreads,
        })
        result = analyzer.detect_spread_anomalies(df)
        assert result["spread_anomaly"].sum() >= 1
