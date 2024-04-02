import time
from datetime import date, datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

from src.config.settings import (
    SBS_BASE_URL,
    SBS_MAX_RETRIES,
    SBS_RATE_LIMIT_SECONDS,
    SBS_REQUEST_TIMEOUT,
    SBS_RETRY_DELAY,
)
from src.utils.logger import setup_logger

logger = setup_logger("scraper.sbs")


class SBSScraper:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; academic-research/1.0)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es-PE,es;q=0.9",
        })
        self._last_request: float = 0

    def scrape_date(self, target_date: date) -> list[dict[str, Any]]:
        self._respect_rate_limit()

        params = {
            "fecha": target_date.strftime("%d/%m/%Y"),
        }

        for attempt in range(1, SBS_MAX_RETRIES + 1):
            try:
                response = self._session.get(
                    SBS_BASE_URL,
                    params=params,
                    timeout=SBS_REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                records = self._parse_html(response.text, target_date)
                logger.info(f"{target_date}: {len(records)} registros")
                return records

            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt} fallido para {target_date}: {e}")
                if attempt < SBS_MAX_RETRIES:
                    time.sleep(SBS_RETRY_DELAY * attempt)

        logger.error(f"No se pudo obtener datos para {target_date}")
        return []

    def scrape_range(self, start: date, end: date) -> list[dict[str, Any]]:
        from src.utils.date_helpers import generate_date_range

        all_records: list[dict] = []
        dates = generate_date_range(start, end)

        logger.info(f"Scrapeando {len(dates)} dias habiles: {start} a {end}")

        for target_date in dates:
            records = self.scrape_date(target_date)
            all_records.extend(records)

        logger.info(f"Total: {len(all_records)} registros de {len(dates)} dias")
        return all_records

    def _parse_html(self, html: str, target_date: date) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        table = soup.find("table", {"id": "ctl00_cphContent_rgTipoCambio"})
        if not table:
            table = soup.find("table", class_="APLI_BASE2")

        if not table:
            return records

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            bank_name = cells[0].get_text(strip=True)
            if not bank_name or bank_name.lower() in ("promedio", "total"):
                continue

            try:
                buy_rate = self._parse_rate(cells[1].get_text(strip=True))
                sell_rate = self._parse_rate(cells[2].get_text(strip=True))
            except (ValueError, IndexError):
                continue

            if buy_rate is None or sell_rate is None:
                continue

            spread = round(sell_rate - buy_rate, 4) if sell_rate and buy_rate else None

            records.append({
                "fecha": target_date,
                "entidad": bank_name,
                "compra": buy_rate,
                "venta": sell_rate,
                "spread": spread,
            })

        return records

    def _parse_rate(self, text: str) -> float | None:
        text = text.strip().replace(",", ".")
        if not text or text == "-" or text == "N/A":
            return None
        try:
            return round(float(text), 4)
        except ValueError:
            return None

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < SBS_RATE_LIMIT_SECONDS:
            time.sleep(SBS_RATE_LIMIT_SECONDS - elapsed)
        self._last_request = time.time()

    def close(self) -> None:
        self._session.close()
