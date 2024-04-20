import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("transform.spread")


class SpreadAnalyzer:
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["spread_pct"] = (df["spread"] / df["compra"] * 100).round(4)

        enriched = []
        for entity, group in df.groupby("entidad"):
            group = group.sort_values("fecha").copy()
            group["compra_var_diaria"] = group["compra"].pct_change() * 100
            group["venta_var_diaria"] = group["venta"].pct_change() * 100
            group["spread_ma_5d"] = group["spread"].rolling(5, min_periods=1).mean()
            group["spread_ma_20d"] = group["spread"].rolling(20, min_periods=5).mean()
            group["volatilidad_5d"] = group["compra"].rolling(5, min_periods=2).std()
            enriched.append(group)

        result = pd.concat(enriched, ignore_index=True)
        logger.info(f"Analisis de spreads: {len(result)} registros enriquecidos")
        return result

    def rank_banks(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        ranking = (
            df.groupby("entidad")
            .agg(
                spread_promedio=("spread", "mean"),
                spread_mediana=("spread", "median"),
                spread_min=("spread", "min"),
                spread_max=("spread", "max"),
                volatilidad_compra=("compra", "std"),
                dias_registrados=("fecha", "nunique"),
            )
            .round(4)
            .sort_values("spread_promedio")
            .reset_index()
        )

        ranking["ranking"] = range(1, len(ranking) + 1)

        logger.info(f"Ranking de {len(ranking)} entidades generado")
        return ranking

    def detect_spread_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["spread_anomaly"] = False

        for entity, group in df.groupby("entidad"):
            mean_spread = group["spread"].mean()
            std_spread = group["spread"].std()

            if std_spread == 0:
                continue

            z_scores = (group["spread"] - mean_spread) / std_spread
            mask = z_scores.abs() > 2.0
            df.loc[mask.index[mask], "spread_anomaly"] = True

        anomaly_count = df["spread_anomaly"].sum()
        logger.info(f"Anomalias de spread: {anomaly_count} de {len(df)}")
        return df
