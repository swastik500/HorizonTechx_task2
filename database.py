"""SQLite persistence for holdings and an immutable transaction ledger."""
import sqlite3
import math
from contextlib import contextmanager
from utils import DB_PATH, timestamp

class Database:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS holdings (
                symbol TEXT PRIMARY KEY, company TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
                purchase_price REAL NOT NULL CHECK(purchase_price > 0), current_price REAL NOT NULL CHECK(current_price > 0),
                updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL, transaction_type TEXT NOT NULL
                CHECK(transaction_type IN ('BUY','SELL')), quantity INTEGER NOT NULL CHECK(quantity > 0),
                price REAL NOT NULL CHECK(price > 0), created_at TEXT NOT NULL)""")

    def holdings(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM holdings ORDER BY symbol")]

    def get(self, symbol):
        with self.connect() as db:
            row = db.execute("SELECT * FROM holdings WHERE symbol=?", (symbol.upper(),)).fetchone()
            return dict(row) if row else None

    def transactions(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM transactions ORDER BY id DESC")]

    def add(self, stock, record_transaction=True):
        now = timestamp()
        with self.connect() as db:
            if db.execute("SELECT 1 FROM holdings WHERE symbol=?", (stock['symbol'],)).fetchone():
                raise ValueError(f"{stock['symbol']} is already in your portfolio. Edit it or record a buy instead.")
            db.execute("INSERT INTO holdings VALUES (?,?,?,?,?,?)", (stock['symbol'],stock['company'],stock['quantity'],stock['purchase_price'],stock['current_price'],now))
            if record_transaction:
                db.execute("INSERT INTO transactions(symbol,transaction_type,quantity,price,created_at) VALUES(?,?,?,?,?)", (stock['symbol'],'BUY',stock['quantity'],stock['purchase_price'],now))

    def edit(self, symbol, stock):
        with self.connect() as db:
            cursor = db.execute("UPDATE holdings SET symbol=?,company=?,quantity=?,purchase_price=?,current_price=?,updated_at=? WHERE symbol=?",
                (stock['symbol'],stock['company'],stock['quantity'],stock['purchase_price'],stock['current_price'],timestamp(),symbol.upper()))
            if cursor.rowcount == 0: raise ValueError("That holding no longer exists.")

    def delete(self, symbol):
        with self.connect() as db: db.execute("DELETE FROM holdings WHERE symbol=?", (symbol.upper(),))

    def trade(self, symbol, kind, quantity, price):
        symbol, kind = symbol.upper(), kind.upper()
        try:
            raw_quantity, price = float(quantity), float(price)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number and price must be a number.") from None
        if not math.isfinite(raw_quantity) or not raw_quantity.is_integer(): raise ValueError("Quantity must be a whole number.")
        quantity = int(raw_quantity)
        if quantity <= 0 or not math.isfinite(price) or price <= 0: raise ValueError("Quantity and price must be greater than zero.")
        now = timestamp()
        with self.connect() as db:
            row = db.execute("SELECT * FROM holdings WHERE symbol=?", (symbol,)).fetchone()
            if kind == "BUY":
                if not row: raise ValueError("Add the company and its name on the Portfolio page first.")
                total_quantity = row['quantity'] + quantity
                average_cost = (row['quantity'] * row['purchase_price'] + quantity * price) / total_quantity
                db.execute("UPDATE holdings SET quantity=?,purchase_price=?,current_price=?,updated_at=? WHERE symbol=?", (total_quantity,average_cost,price,now,symbol))
            elif kind == "SELL":
                if not row or quantity > row['quantity']: raise ValueError("You cannot sell more shares than you own.")
                if quantity == row['quantity']: db.execute("DELETE FROM holdings WHERE symbol=?", (symbol,))
                else: db.execute("UPDATE holdings SET quantity=?,current_price=?,updated_at=? WHERE symbol=?", (row['quantity']-quantity,price,now,symbol))
            else: raise ValueError("Transaction type must be BUY or SELL.")
            db.execute("INSERT INTO transactions(symbol,transaction_type,quantity,price,created_at) VALUES(?,?,?,?,?)", (symbol,kind,quantity,price,now))

    def import_holdings(self, stocks):
        """Validate the whole import before writing; merge duplicate symbols by replacement."""
        now = timestamp()
        with self.connect() as db:
            for s in stocks:
                db.execute("INSERT INTO holdings VALUES(?,?,?,?,?,?) ON CONFLICT(symbol) DO UPDATE SET company=excluded.company,quantity=excluded.quantity,purchase_price=excluded.purchase_price,current_price=excluded.current_price,updated_at=excluded.updated_at",
                    (s['symbol'],s['company'],s['quantity'],s['purchase_price'],s['current_price'],now))

    def reset(self):
        with self.connect() as db:
            db.execute("DELETE FROM holdings")
            db.execute("DELETE FROM transactions")

    def seed(self, stocks):
        with self.connect() as db:
            if db.execute("SELECT 1 FROM holdings LIMIT 1").fetchone(): raise ValueError("Sample data can only be added to an empty portfolio.")
        for stock in stocks: self.add(stock)
