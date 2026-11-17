# Northstar Stock Portfolio Tracker

A local desktop portfolio manager written for Python 3.11+. It uses CustomTkinter for a dark desktop interface, SQLite for holdings and trade history, Matplotlib for charts, and Pandas for CSV import and export. No live market feed or API key is used.

## Features

- Dashboard cards for invested amount, current value, total profit/loss, shares, and companies.
- Portfolio allocation and per-stock performance charts.
- Add, edit, search, filter, refresh, and remove holdings.
- A transaction ledger. BUY trades update the weighted average cost; SELL trades reduce shares and reject overselling. A fully sold position is removed, while its transaction records remain.
- Local SQLite persistence in `data/portfolio.db`.
- CSV import/export and a TXT portfolio report from Settings.
- Sample holdings, top and worst performers, and a confirmed reset action.
- Supported symbols have convenient **sample** prices. Prices are not live quotes and can be changed manually.

## Install

In the VS Code terminal, open this project folder and create a virtual environment:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, call the virtual environment's Python directly instead:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run in VS Code

1. Open this project folder in VS Code.
2. Select the project `venv` interpreter (or Python 3.11+ with the requirements installed).
3. Open `main.py` and select **Run Python File**, or run:

```powershell
python main.py
```

If the virtual environment is not activated, use its Python directly:

```powershell
.\venv\Scripts\python.exe main.py
```

The app creates `data/` and `exports/` as needed. Your database stays local to this project. Use **Settings → Load sample portfolio** to populate a fresh install; sample prices are for demonstration only.

## CSV format

Imports require a header row containing `symbol`, `company`, `quantity`, `purchase_price`, and `current_price`. Prices are per share. For an existing symbol, import replaces that holding; it does not create a trade record. The full file is validated before any rows are written.

## Project layout

```text
main.py             App entry point
database.py         SQLite holdings and transactions
portfolio.py        Portfolio calculations
stock_data.py       Sample prices and company names
charts.py           Matplotlib dashboard charts
utils.py            Validation, formatting, and paths
ui/app.py           CustomTkinter screens and interactions
data/               Local SQLite database
exports/            Suggested folder for exported files
requirements.txt    Python dependencies
```

## Author

Created by **swastik**.

## Disclaimer

Prices in this app are sample values for demonstration only. They are not live quotes and must not be used for trading or investment decisions.
