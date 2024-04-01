# Scraper de Tipo de Cambio - SBS/SUNAT Perú

¿Sabías que la diferencia entre lo que un banco te cobra al venderte dólares y lo que te paga al comprártelos puede variar hasta 3 veces entre entidades financieras del mismo país?

En el Perú, cada banco fija su propio tipo de cambio de compra y venta. La SBS publica diariamente las cotizaciones de todas las entidades del sistema financiero, pero estos datos no están disponibles de forma estructurada para análisis comparativo.

Soy Gian Cruz. Construí este scraper para extraer, limpiar y analizar el tipo de cambio bancario publicado por la SBS y la SUNAT, calcular los spreads de cada entidad y detectar anomalías en el margen cambiario.

## ¿Qué hace este proyecto?

- **Extrae** las cotizaciones diarias de tipo de cambio desde la SBS y la SUNAT
- **Limpia** y estandariza los nombres de las entidades financieras
- **Calcula** el spread (margen) de cada banco y su evolución temporal
- **Ranking** de bancos por spread promedio (¿quién cobra menos?)
- **Detecta anomalías** en los spreads que podrían indicar movimientos inusuales
- **Exporta** los datos procesados en CSV para análisis posterior

## Hallazgos

- Los bancos grandes (BCP, BBVA, Scotiabank) mantienen spreads más estables
- Las entidades especializadas en microfinanzas muestran mayor volatilidad en sus márgenes
- En períodos de inestabilidad política, los spreads de todas las entidades se amplían simultáneamente

## Stack tecnológico

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.12 |
| Web scraping | requests, BeautifulSoup4 |
| Procesamiento | pandas, numpy |
| Visualización | matplotlib, seaborn |
| Testing | pytest |

## Instalación

```bash
git clone https://github.com/giansocial/scraper-sbs-peru.git
cd scraper-sbs-peru
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Scraper SUNAT (tipo de cambio oficial, por año)
python -m src.pipeline --source sunat --year 2024

# Scraper SBS (cotizaciones bancarias, por rango de fechas)
python -m src.pipeline --source sbs --start 2024-10-01 --end 2024-10-31
```

## Estructura del proyecto

```
scraper-sbs-peru/
├── src/
│   ├── config/          # Configuración y URLs
│   ├── scraper/         # Scrapers SBS y SUNAT
│   ├── transform/       # Limpieza y análisis de spreads
│   ├── load/            # Exportación CSV
│   ├── utils/           # Logger y helpers de fechas
│   └── pipeline.py      # Orquestador principal
├── tests/               # Tests unitarios
├── notebooks/           # Análisis exploratorio
├── data/                # Datos crudos y procesados
└── docs/                # Documentación
```

## Tests

```bash
pytest -v
```

## Licencia

MIT

---

# Exchange Rate Scraper - SBS/SUNAT Peru

Did you know the spread between buying and selling dollars can vary up to 3x between banks in Peru?

I'm Gian Cruz. I built this scraper to extract, clean and analyze exchange rates published by Peru's banking regulator (SBS) and tax authority (SUNAT), calculate bank spreads, and detect anomalies in exchange rate margins.

## Quick start

```bash
git clone https://github.com/giansocial/scraper-sbs-peru.git
cd scraper-sbs-peru
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline --source sunat --year 2024
```

## License

MIT
