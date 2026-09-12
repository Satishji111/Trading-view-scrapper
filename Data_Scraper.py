import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from tvDatafeed import TvDatafeed, Interval
from pathlib import Path
import pandas as pd
import threading
import sys
import time


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FOLDER = Path("Output")
DATA_FOLDER = OUTPUT_FOLDER / "Data"
REPORT_FOLDER = OUTPUT_FOLDER / "Reports"

DATA_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

INTERVALS = {
    "1 Minbar": Interval.in_1_minute,
    "3 Minbar": Interval.in_3_minute,
    "5 Minbar": Interval.in_5_minute,
    "15 Minbar": Interval.in_15_minute,
    "30 Minbar": Interval.in_30_minute,
    "1 Hour": Interval.in_1_hour,
    "Daybar": Interval.in_daily,
}
MAX_RETRIES = 3
cancel_event = threading.Event()


def resource_path(filename):
    """Return the path to a bundled resource or a source-tree resource."""

    bundle_folder = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(bundle_folder) / filename


# ============================================================
# FETCH DATA FUNCTION
# ============================================================

def fetch_data():
    """
    Fetch historical data for all entered symbols.
    Runs in a background thread so that the GUI does not freeze.
    """

    # --------------------------------------------------------
    # Get and validate ticker input
    # --------------------------------------------------------

    ticker_input = ticker_entry.get().strip()

    if not ticker_input:
        messagebox.showerror(
            "Input Error",
            "Please enter at least one ticker."
        )
        return

    # Remove spaces and empty values
    Symbols = [
        symbol.strip().upper()
        for symbol in ticker_input.split(",")
        if symbol.strip()
    ]

    # Remove duplicate symbols while preserving order
    Symbols = list(dict.fromkeys(Symbols))

    # --------------------------------------------------------
    # Get and validate exchange
    # --------------------------------------------------------

    Exchange = exchange_entry.get().strip().upper()

    if not Exchange:
        messagebox.showerror(
            "Input Error",
            "Please enter the Exchange Code."
        )
        return

    # --------------------------------------------------------
    # Get bar type and validate number of bars
    # --------------------------------------------------------

    Bar_type = bar_type_entry.get().strip()

    if Bar_type not in INTERVALS:
        messagebox.showerror(
            "Input Error",
            "Please select a valid bar type."
        )
        return

    try:
        Bars = int(days_entry.get().strip())

        if Bars <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Please enter a positive number of days."
        )
        return

    # --------------------------------------------------------
    # Disable button while process is running
    # --------------------------------------------------------

    process_button.config(state="disabled")
    cancel_button.config(state="normal")
    cancel_event.clear()
    status_label.config(text="Starting data fetch...")
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(Symbols)

    # Start background thread
    thread = threading.Thread(
        target=process_symbols,
        args=(Symbols, Exchange, Bars, Bar_type),
        daemon=True
    )

    thread.start()


# ============================================================
# PROCESS SYMBOLS
# ============================================================

def process_symbols(Symbols, Exchange, Bars, Bar_type):
    """
    Process all symbols one by one.
    """

    successful_symbols = []
    failed_symbols = []

    try:
        # Create TradingView connection only once
        tv = TvDatafeed()

        total_symbols = len(Symbols)

        for index, Symbol in enumerate(Symbols, start=1):

            if cancel_event.is_set():
                break

            # Update GUI safely using root.after()
            root.after(
                0,
                update_progress,
                index,
                total_symbols,
                Symbol
            )

            try:
                # ------------------------------------------------
                # Fetch historical data
                # ------------------------------------------------

                data = fetch_with_retries(
                    tv,
                    Symbol,
                    Exchange,
                    INTERVALS[Bar_type],
                    Bars
                )

                if cancel_event.is_set():
                    break

                # ------------------------------------------------
                # Check whether data was returned
                # ------------------------------------------------

                if data is None or data.empty:

                    failed_symbols.append({
                        "Symbol": Symbol,
                        "Exchange": Exchange,
                        "Status": "No Data",
                        "Error": "No historical data returned"
                    })

                    continue

                # ------------------------------------------------
                # Convert to DataFrame
                # ------------------------------------------------

                df = pd.DataFrame(data)
                symbol_value = f"{Exchange}:{Symbol}"

                if "symbol" in df.columns:
                    df["symbol"] = symbol_value
                    df = df[["symbol"] + [
                        column for column in df.columns if column != "symbol"
                    ]]
                else:
                    df.insert(0, "symbol", symbol_value)

                # ------------------------------------------------
                # Convert datetime safely
                # ------------------------------------------------

                datetime_index = pd.to_datetime(df.index, errors="coerce")

                if datetime_index.isna().any():
                    raise ValueError("One or more invalid datetime values returned")

                if Bar_type == "Daybar":
                    df.index = datetime_index.strftime("%Y-%m-%d")
                else:
                    df.index = datetime_index.strftime("%Y-%m-%d %H:%M:%S")

                df.index.name = "datetime"
                # ------------------------------------------------
                # Create safe filename
                # ------------------------------------------------

                safe_symbol = Symbol.replace("/", ".").replace("\\", ".")
                file_name = f"{Exchange}_{safe_symbol}_{Bar_type.replace(' ', '_')}.csv"

                output_file = DATA_FOLDER / file_name

                # ------------------------------------------------
                # Save CSV
                # ------------------------------------------------

                df.to_csv(
                    output_file,
                    index=True
                )

                successful_symbols.append(Symbol)

            except Exception as e:

                failed_symbols.append({
                    "Symbol": Symbol,
                    "Exchange": Exchange,
                    "Status": "Error",
                    "Error": str(e)
                })

        # --------------------------------------------------------
        # Save failed-symbol report
        # --------------------------------------------------------

        failed_report = REPORT_FOLDER / "Failed_Symbols.csv"

        if failed_symbols:

            failed_df = pd.DataFrame(failed_symbols)

            failed_df.to_csv(
                failed_report,
                index=False
            )

        else:

            # Remove old report if there are no failures
            if failed_report.exists():
                failed_report.unlink()

        # --------------------------------------------------------
        # Save scraping summary
        # --------------------------------------------------------

        summary = pd.DataFrame([{
            "Total Symbols": total_symbols,
            "Successful": len(successful_symbols),
            "Failed": len(failed_symbols),
            "Exchange": Exchange,
            "Number of Bars": Bars,
            "Bar Type": Bar_type
        }])

        summary_file = REPORT_FOLDER / "Scraping_Summary.csv"

        summary.to_csv(
            summary_file,
            index=False
        )

        # --------------------------------------------------------
        # Show completion message
        # --------------------------------------------------------

        root.after(
            0,
            process_completed,
            total_symbols,
            len(successful_symbols),
            len(failed_symbols),
            failed_report,
            cancel_event.is_set()
        )

    except Exception as e:

        root.after(
            0,
            process_failed,
            str(e)
        )


def fetch_with_retries(tv, symbol, exchange, interval, bars):
    """Fetch one symbol, retrying temporary TradingView failures."""

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        if cancel_event.is_set():
            return None

        try:
            return tv.get_hist(
                symbol,
                exchange,
                interval=interval,
                n_bars=bars
            )
        except Exception as error:
            last_error = error
            if attempt < MAX_RETRIES:
                time.sleep(2)

    raise RuntimeError(
        f"Failed after {MAX_RETRIES} attempts: {last_error}"
    )


# ============================================================
# UPDATE PROGRESS
# ============================================================

def update_progress(current, total, symbol):
    """
    Update progress bar and status text.
    """

    progress_bar["value"] = current

    percentage = (current / total) * 100

    status_label.config(
        text=f"Processing: {current}/{total} "
             f"({percentage:.1f}%) | Current: {symbol}"
    )

    root.update_idletasks()


# ============================================================
# PROCESS COMPLETED
# ============================================================

def process_completed(
    total_symbols,
    successful,
    failed,
    failed_report,
    cancelled
):

    process_button.config(state="normal")
    cancel_button.config(state="disabled")

    progress_bar["value"] = progress_bar["maximum"]

    status_label.config(
        text="Process cancelled." if cancelled else "Process completed successfully."
    )

    if failed > 0:

        messagebox.showinfo(
            "Process Completed",
            f"Total Symbols: {total_symbols}\n"
            f"Successful: {successful}\n"
            f"Failed: {failed}\n\n"
            f"Data saved in:\n"
            f"{DATA_FOLDER}\n\n"
            f"Failed symbol report saved in:\n"
            f"{failed_report}"
        )

    else:

        messagebox.showinfo(
            "Process Completed",
            f"Total Symbols: {total_symbols}\n"
            f"Successful: {successful}\n"
            f"Failed: {failed}\n\n"
            f"All data was successfully retrieved.\n\n"
            f"Data saved in:\n"
            f"{DATA_FOLDER}"
        )


# ============================================================
# PROCESS FAILED
# ============================================================

def process_failed(error_message):

    process_button.config(state="normal")
    cancel_button.config(state="disabled")

    status_label.config(
        text="Process failed."
    )

    messagebox.showerror(
        "Process Error",
        f"The scraping process could not be completed.\n\n"
        f"Error:\n{error_message}"
    )


# ============================================================
# CLEAR INPUTS
# ============================================================

def clear_fields():

    ticker_entry.delete(0, tk.END)
    exchange_entry.delete(0, tk.END)
    bar_type_entry.set("Daybar")
    days_entry.delete(0, tk.END)

    progress_bar["value"] = 0

    status_label.config(
        text="Ready"
    )


def cancel_fetch():
    """Request cancellation after the current network request finishes."""

    cancel_event.set()
    cancel_button.config(state="disabled")
    status_label.config(text="Cancelling after current request...")


# ============================================================
# TKINTER GUI
# ============================================================

root = tk.Tk()

root.title("TradingView Data Scraper")
root.geometry("500x500")

root.resizable(False, False)


# ============================================================
# BACKGROUND IMAGE
# ============================================================

try:

    bg_image = Image.open(resource_path("logo.png"))

    bg_image = bg_image.resize(
        (500, 500),
        Image.Resampling.LANCZOS
    )

    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(
        root,
        width=500,
        height=500
    )

    canvas.pack(
        fill="both",
        expand=True
    )

    canvas.create_image(
        0,
        0,
        image=bg_photo,
        anchor="nw"
    )

except Exception:

    # If logo.png is not available,
    # create a plain background.

    canvas = tk.Canvas(
        root,
        width=500,
        height=500,
        bg="#F0F0F0"
    )

    canvas.pack(
        fill="both",
        expand=True
    )


# ============================================================
# TICKER
# ============================================================

ticker_label = tk.Label(
    root,
    text="Enter Ticker(s):",
    bg="#F0F0F0",
    fg="black"
)

ticker_entry = tk.Entry(
    root,
    width=45
)

canvas.create_window(
    250,
    45,
    window=ticker_label
)

canvas.create_window(
    250,
    75,
    window=ticker_entry
)


# ============================================================
# EXCHANGE
# ============================================================

exchange_label = tk.Label(
    root,
    
    text="Enter Exchange Code (At TradingView):",
    bg="#F0F0F0",
    fg="black"
)

exchange_entry = tk.Entry(
    root,
    width=45
)

canvas.create_window(
    250,
    110,
    window=exchange_label
)

canvas.create_window(
    250,
    140,
    window=exchange_entry
)


# ============================================================
# BAR TYPE
# ============================================================

bar_type_label = tk.Label(
    root,
    text="Select Bar Type:",
    bg="#F0F0F0",
    fg="black"
)

bar_type_entry = ttk.Combobox(
    root,
    values=list(INTERVALS),
    state="readonly",
    width=42
)
bar_type_entry.set("Daybar")

canvas.create_window(
    250,
    175,
    window=bar_type_label
)

canvas.create_window(
    250,
    205,
    window=bar_type_entry
)


# ============================================================
# NUMBER OF BARS
# ============================================================

days_label = tk.Label(
    root,
    text="Enter Number of Bars:",
    bg="#F0F0F0",
    fg="black"
)

days_entry = tk.Entry(
    root,
    width=45
)

canvas.create_window(
    250,
    240,
    window=days_label
)

canvas.create_window(
    250,
    270,
    window=days_entry
)


# ============================================================
# FETCH BUTTON
# ============================================================

process_button = tk.Button(
    root,
    text="Fetch Data",
    bg="#4CAF50",
    fg="white",
    width=15,
    command=fetch_data
)

canvas.create_window(
    190,
    315,
    window=process_button
)


# ============================================================
# CLEAR BUTTON
# ============================================================

clear_button = tk.Button(
    root,
    text="Clear",
    width=15,
    command=clear_fields
)

canvas.create_window(
    310,
    315,
    window=clear_button
)


# ============================================================
# CANCEL BUTTON
# ============================================================

cancel_button = tk.Button(
    root,
    text="Cancel",
    width=15,
    state="disabled",
    command=cancel_fetch
)

canvas.create_window(
    250,
    345,
    window=cancel_button
)


# ============================================================
# PROGRESS BAR
# ============================================================

progress_bar = ttk.Progressbar(
    root,
    orient="horizontal",
    length=350,
    mode="determinate"
)

canvas.create_window(
    250,
    385,
    window=progress_bar
)


# ============================================================
# STATUS LABEL
# ============================================================

status_label = tk.Label(
    root,
    text="Ready",
    bg="#F0F0F0",
    fg="black"
)

canvas.create_window(
    250,
    420,
    window=status_label
)


# ============================================================
# OUTPUT INFORMATION
# ============================================================

output_label = tk.Label(
    root,
    text="Output: Output/Data    |    Reports: Output/Reports",
    bg="#F0F0F0",
    fg="black",
    font=("Arial", 8)
)

canvas.create_window(
    250,
    460,
    window=output_label
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()