import time
from datetime import date
from typing import Any

import requests

from src.config.settings import (
    SUNAT_TC_URL,
    SBS_MAX_RETRIES,
    SBS_RATE_LIMIT_SECONDS,
    SBS_REQUEST_TIMEOUT,
    SBS_RETRY_DELAY,
)
from src.utils.logger import setup_logger

logger = setup_logger("scraper.sunat")


class SUNATScraper:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._last_request: float = 0

    def fetch_monthly_rates(self, year: int, month: int) -> list[dict[str, Any]]:
        self._respect_rate_limit()

        params = {
            "anio": str(year),
            "mes": f"{month:02d}",
            "tipo": "USD",
        }

        for attempt in range(1, SBS_MAX_RETRIES + 1):
            try:
                response = self._session.get(
                    SUNAT_TC_URL,
                    params=params,
                    timeout=SBS_REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                records = self._parse_response(response.json(), year, month)
                logger.info(f"SUNAT {year}-{month:02d}: {len(records)} registros")
                return records

            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt} fallido: {e}")
                if attempt < SBS_MAX_RETRIES:
                    time.sleep(SBS_RETRY_DELAY * attempt)
            except (ValueError, KeyError) as e:
                logger.error(f"Error parseando respuesta SUNAT: {e}")
                return []

        return []

    def fetch_year(self, year: int) -> list[dict[str, Any]]:
        all_records: list[dict] = []

        for month in range(1, 13):
            records = self.fetch_monthly_rates(year, month)
            all_records.extend(records)

        logger.info(f"SUNAT {year}: {len(all_records)} registros totales")
        return all_records

    def _parse_response(
        self, data: list[dict], year: int, month: int
    ) -> list[dict[str, Any]]:
        records = []

        for entry in data:
            try:
                day = int(entry.get("dia", 0))
                if day < 1 or day > 31:
                    continue

                buy_rate = float(entry.get("compra", 0))
                sell_rate = float(entry.get("venta", 0))

                if buy_rate <= 0 or sell_rate <= 0:
                    continue

                records.append({
                    "fecha": date(year, month, day),
                    "entidad": "SUNAT",
                    "compra": round(buy_rate, 4),
                    "venta": round(sell_rate, 4),
                    "spread": round(sell_rate - buy_rate, 4),
                })
            except (ValueError, TypeError):
                continue

        return records

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < SBS_RATE_LIMIT_SECONDS:
            time.sleep(SBS_RATE_LIMIT_SECONDS - elapsed)
        self._last_request = time.time()

    def close(self) -> None:
        self._session.close()
