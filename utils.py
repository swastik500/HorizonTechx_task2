"""Shared validation, formatting, and file helpers."""
from datetime import datetime
import math
from pathlib import Path
import re

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
EXPORT_DIR = APP_DIR / "exports"
for _directory in (DATA_DIR, EXPORT_DIR):
    _directory.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "portfolio.db"

def validate_stock(symbol, company, quantity, purchase_price, current_price):
    symbol = str(symbol).strip().upper()
    company = str(company).strip()
    if not symbol or not re.fullmatch(r"[A-Z0-9.\-]{1,12}", symbol):
        raise ValueError("Enter a valid stock symbol (letters, numbers, . or -).")
    if not company:
        raise ValueError("Company name cannot be empty.")
    try:
        raw_quantity = float(quantity)
        purchase_price, current_price = float(purchase_price), float(current_price)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a whole number and prices must be numbers.") from None
    if not math.isfinite(raw_quantity) or not raw_quantity.is_integer():
        raise ValueError("Quantity must be a whole number.")
    quantity = int(raw_quantity)
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    if not math.isfinite(purchase_price) or not math.isfinite(current_price) or purchase_price <= 0 or current_price <= 0:
        raise ValueError("Prices must be greater than zero.")
    return {"symbol": symbol, "company": company, "quantity": quantity,
            "purchase_price": purchase_price, "current_price": current_price}

def money(value):
    return f"${value:,.2f}"

def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")
