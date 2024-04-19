import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

SBS_BASE_URL = "https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx"

SBS_REQUEST_TIMEOUT = 15
SBS_MAX_RETRIES = 3
SBS_RETRY_DELAY = 2.0
SBS_RATE_LIMIT_SECONDS = 2.0

SUNAT_TC_URL = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"

BANKS = [
    "B. Continental",
    "B. de Comercio",
    "B. de Credito del Peru",
    "B. Interamericano de Finanzas",
    "B. Pichincha",
    "Scotiabank Peru",
    "Interbank",
    "MiBanco",
    "B. GNB",
    "B. Falabella Peru",
    "B. Ripley",
    "B. Santander Peru",
]
