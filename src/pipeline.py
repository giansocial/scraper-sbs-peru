import argparse
from datetime import date, datetime, timedelta

import pandas as pd

from src.scraper.sbs_scraper import SBSScraper
from src.scraper.sunat_scraper import SUNATScraper
from src.transform.cleaner import ExchangeRateCleaner
from src.transform.spread_analyzer import SpreadAnalyzer
from src.load.csv_exporter import CSVExporter
from src.utils.logger import setup_logger

logger = setup_logger("pipeline")


class ExchangeRatePipeline:
    def __init__(self) -> None:
        self.sbs_scraper = SBSScraper()
        self.sunat_scraper = SUNATScraper()
        self.cleaner = ExchangeRateCleaner()
        self.analyzer = SpreadAnalyzer()
        self.exporter = CSVExporter()

    def run(
        self,
        source: str = "sunat",
        start: date | None = None,
        end: date | None = None,
        year: int | None = None,
    ) -> None:
        start_time = datetime.now()
        logger.info(f"Pipeline iniciado: {start_time.isoformat()}")
        logger.info(f"Fuente: {source}")

        try:
            df = self._extract(source, start, end, year)
            if df.empty:
                logger.warning("Sin datos para procesar")
                return

            df = self._transform(df)
            self._load(df, source)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Pipeline completado en {elapsed:.1f}s")

        except Exception as e:
            logger.error(f"Pipeline fallido: {e}")
            raise
        finally:
            self.sbs_scraper.close()
            self.sunat_scraper.close()

    def _extract(
        self, source: str, start: date | None, end: date | None, year: int | None
    ) -> pd.DataFrame:
        logger.info("ETAPA 1: Extraccion")

        if source == "sbs":
            if not start or not end:
                end = date.today()
                start = end - timedelta(days=30)
            records = self.sbs_scraper.scrape_range(start, end)
        elif source == "sunat":
            target_year = year or date.today().year
            records = self.sunat_scraper.fetch_year(target_year)
        else:
            raise ValueError(f"Fuente no soportada: {source}")

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        self.exporter.save_raw(df, f"raw_{source}_{datetime.now():%Y%m%d}.csv")
        return df

    def _transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("ETAPA 2: Transformacion")

        df = self.cleaner.clean(df)
        df = self.cleaner.standardize_bank_names(df)
        df = self.analyzer.analyze(df)
        df = self.analyzer.detect_spread_anomalies(df)

        return df

    def _load(self, df: pd.DataFrame, source: str) -> None:
        logger.info("ETAPA 3: Carga")

        self.exporter.save_processed(df, f"tipo_cambio_{source}.csv")

        ranking = self.analyzer.rank_banks(df)
        if not ranking.empty:
            self.exporter.save_processed(ranking, f"ranking_bancos_{source}.csv")

        anomalies = df[df.get("spread_anomaly", False) == True]
        if not anomalies.empty:
            self.exporter.save_processed(anomalies, f"anomalias_{source}.csv")
            logger.info(f"Anomalias detectadas: {len(anomalies)}")


def main():
    parser = argparse.ArgumentParser(
        description="Scraper de Tipo de Cambio - SBS/SUNAT Peru"
    )
    parser.add_argument(
        "--source",
        choices=["sbs", "sunat"],
        default="sunat",
        help="Fuente de datos",
    )
    parser.add_argument("--year", type=int, help="Anio a scrapear (SUNAT)")
    parser.add_argument("--start", type=str, help="Fecha inicio YYYY-MM-DD (SBS)")
    parser.add_argument("--end", type=str, help="Fecha fin YYYY-MM-DD (SBS)")
    args = parser.parse_args()

    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None

    pipeline = ExchangeRatePipeline()
    pipeline.run(source=args.source, start=start, end=end, year=args.year)


if __name__ == "__main__":
    main()
