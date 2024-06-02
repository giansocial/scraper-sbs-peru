from pathlib import Path

import pandas as pd

from src.config.settings import PROCESSED_DIR, RAW_DIR
from src.utils.logger import setup_logger

logger = setup_logger("load.exporter")


class CSVExporter:
    def save_raw(self, df: pd.DataFrame, filename: str) -> Path:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        filepath = RAW_DIR / filename
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"Raw guardado: {filepath} ({len(df)} filas)")
        return filepath

    def save_processed(self, df: pd.DataFrame, filename: str) -> Path:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        filepath = PROCESSED_DIR / filename
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"Procesado guardado: {filepath} ({len(df)} filas)")
        return filepath
