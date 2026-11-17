"""Start the Northstar Stock Portfolio Tracker."""
from tkinter import messagebox
from ui.app import run

if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        try: messagebox.showerror("Northstar could not start",f"{exc}\n\nCheck that the required packages are installed.")
        except Exception: print(f"Northstar could not start: {exc}")
