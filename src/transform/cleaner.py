import pandas as pd

from src.utils.logger import setup_logger

logger = setup_logger("transform.cleaner")


class ExchangeRateCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        initial = len(df)
        df = df.drop_duplicates(subset=["fecha", "entidad"])
        dropped = initial - len(df)
        if dropped > 0:
            logger.info(f"Eliminados {dropped} duplicados")

        df["entidad"] = df["entidad"].str.strip()

        df = df[df["compra"] > 0]
        df = df[df["venta"] > 0]
        df = df[df["venta"] >= df["compra"]]

        removed = initial - len(df) - dropped
        if removed > 0:
            logger.info(f"Eliminados {removed} registros con tasas invalidas")

        df = df.sort_values(["entidad", "fecha"]).reset_index(drop=True)

        logger.info(f"Limpieza: {len(df)} registros validos de {initial} originales")
        return df

    def standardize_bank_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        name_map = {
            "B. Continental": "BBVA Continental",
            "B. de Credito del Peru": "BCP",
            "B. de Credito del Perú": "BCP",
            "B. Interamericano de Finanzas": "BanBif",
            "Scotiabank Peru": "Scotiabank",
            "Scotiabank Perú": "Scotiabank",
            "B. Pichincha": "Banco Pichincha",
            "B. Falabella Peru": "Banco Falabella",
            "B. Falabella Perú": "Banco Falabella",
            "B. Ripley": "Banco Ripley",
            "B. Santander Peru": "Santander",
            "B. Santander Perú": "Santander",
            "B. GNB": "Banco GNB",
            "B. de Comercio": "Banco de Comercio",
        }

        df["entidad_estandar"] = df["entidad"].map(name_map).fillna(df["entidad"])
        return df
