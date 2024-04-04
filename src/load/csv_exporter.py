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

    def load_existing(self, filename: str, directory: str = "processed") -> pd.DataFrame:
        base = PROCESSED_DIR if directory == "processed" else RAW_DIR
        filepath = base / filename
        if not filepath.exists():
            return pd.DataFrame()
        df = pd.read_csv(filepath, parse_dates=["fecha"])
        logger.info(f"Cargado: {filepath} ({len(df)} filas)")
        return df

    def append_new_records(
        self, existing: pd.DataFrame, new: pd.DataFrame
    ) -> pd.DataFrame:
        if existing.empty:
            return new
        if new.empty:
            return existing

        combined = pd.concat([existing, new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["fecha", "entidad"])
        combined = combined.sort_values(["entidad", "fecha"]).reset_index(drop=True)

        added = len(combined) - len(existing)
        logger.info(f"Append: {added} registros nuevos, {len(combined)} total")
        return combined
