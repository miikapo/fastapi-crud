from pydantic import UUID4
from decimal import Decimal
from datetime import date


DEFAULT_TYPE_MAP = {"UUID": UUID4, "VARCHAR": str, "INTEGER": int, "NUMERIC": Decimal, "DATE": date}
