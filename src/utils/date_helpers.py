from datetime import date, timedelta


MONTH_NAMES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def get_month_name(month: int) -> str:
    if month < 1 or month > 12:
        return ""
    return MONTH_NAMES_ES[month]


def generate_date_range(start: date, end: date) -> list[date]:
    dates = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def format_sbs_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def parse_sbs_date(date_str: str) -> date | None:
    try:
        parts = date_str.strip().split("/")
        return date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, IndexError):
        return None


def is_business_day(d: date) -> bool:
    return d.weekday() < 5
