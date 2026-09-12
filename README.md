# TradingView Data Scraper

A Python-based desktop application that fetches historical market data from TradingView using `tvDatafeed` and saves the results as CSV files.

The application provides a simple Tkinter GUI where users can enter multiple ticker symbols, select an exchange and bar interval, specify the number of historical bars, and fetch the data without freezing the interface.

## Features

- Fetch historical market data from TradingView
- Supports multiple ticker symbols in one request
- Supports multiple time intervals:
  - 1 Minute
  - 3 Minutes
  - 5 Minutes
  - 15 Minutes
  - 30 Minutes
  - 1 Hour
  - Daily
- Duplicate ticker removal
- Automatic ticker and exchange formatting
- Handles inactive or unavailable symbols without stopping the complete process
- Retry mechanism for temporary TradingView request failures
- Background processing using Python threading
- Progress bar with current ticker and completion percentage
- Cancel button to stop the process after the current request
- Failed-symbol report with error details
- Scraping summary report
- Separate folders for downloaded data and reports
- Optional background logo/image for the GUI
- Can be packaged as a standalone Windows executable using PyInstaller

## Technologies Used

- Python
- Tkinter
- Pandas
- Pillow
- tvDatafeed
- pathlib
- threading

## Project Structure

```text
Trading-view-scrapper/
│
├── scraper.py
├── logo.png
│
└── Output/
    ├── Data/
    │   ├── NSE_RELIANCE_Daybar.csv
    │   ├── NSE_TCS_Daybar.csv
    │   └── ...
    │
    └── Reports/
        ├── Failed_Symbols.csv
        └── Scraping_Summary.csv
        
```    
        

# Installation
## 1. Clone the repository

```text
git clone https://github.com/Satishji111/Trading-view-scrapper.git
cd Trading-view-scrapper
```

## 2. Create a virtual environment
```text
python -m venv venv
```

Activate it on Windows:
```text
venv\\Scripts\\activate
```
## 3. Install required packages
```text
pip install pandas pillow tvdatafeed
```
If your tvDatafeed package is installed from a specific fork or source, install the version you normally use for this project.

# Running the Application

Run the Python script:
```text
pip install pandas pillow tvdatafeed
```
The GUI will open.

Enter the required details:

# Ticker(s)

Multiple tickers can be entered using commas.

Example:
```text
RELIANCE,HDFCBANK,TCS,INFY
```
The application automatically removes extra spaces and duplicate symbols.

# Exchange

Enter the exchange code used by TradingView.

Examples:
```text
NSE
BSE
```
# Bar Type

Select one of the available intervals:
```text
1 Minbar
3 Minbar
5 Minbar
15 Minbar
30 Minbar
1 Hour
Daybar
```
# Number of Bars

Enter the number of historical bars required.

Example:
```text
500
```
Then click Fetch Data.

# Output

Downloaded data is saved inside:
```text
Output/Data/
```
For example:
```text
NSE_RELIANCE_Daybar.csv
NSE_TCS_Daybar.csv
```
For daily data, the datetime values are saved in:
```text
YYYY-MM-DD
```
For intraday data, the datetime values are saved in:
```text
YYYY-MM-DD HH:MM:SS
```
# Reports
## Failed_Symbols.csv

If a symbol cannot be downloaded, it is recorded in:
```text
Output/Reports/Failed_Symbols.csv
```
The report contains:

1. Symbol
2. Exchange
3. Status
4. Error

Example:
```text
Symbol,Exchange,Status,Error
ABC,NSE,No Data,No historical data returned
XYZ,NSE,Error,Failed after 3 attempts: ...
```
# Scraping_Summary.csv

A summary of each scraping process is saved in:
```text
Output/Reports/Scraping_Summary.csv
```
It contains:

Total Symbols
Successful
Failed
Exchange
Number of Bars
Bar Type

# Error Handling

The application is designed so that an individual symbol failure does not stop the entire scraping process.

For each ticker:

The application requests historical data.
If the request temporarily fails, it retries up to 3 times.
If no data is returned, the symbol is recorded as failed.
If an unexpected error occurs, the error is recorded.
The application continues processing the remaining symbols.

# Cancellation

The Cancel button allows the user to request cancellation while the scraper is running.

The application completes the current network request and then stops processing additional symbols.

# GUI Progress

While the scraper is running, the application displays:
```text
Processing: 25/100 (25.0%) | Current: RELIANCE
```
This allows the user to monitor the progress of large scraping jobs.

Data Fields

The downloaded CSV files generally contain fields such as:
```text
datetime
symbol
open
high
low
close
volume
```
The exact fields depend on the data returned by tvDatafeed.

# Important Notes

This project depends on the availability and behavior of TradingView and the tvDatafeed library.

Historical data availability can vary by:

Exchange
Symbol
Time interval
Number of requested bars
TradingView data availability

An invalid, inactive, or unavailable symbol may return no data.

The project should be used in accordance with TradingView's terms and any applicable data usage restrictions.

# Packaging as Windows EXE

The application can be packaged using PyInstaller.

Install PyInstaller:
```text
pip install pyinstaller
```
Then build the executable:
```text
pyinstaller --onefile --windowed --clean --add-data "C:\Users\syada11\TradingView\logo.png;." --icon="C:\Users\syada11\TradingView\data_display.ico" "C:\Users\syada11\TradingView\Data_Scraper.py"
```
The executable will be created inside:
```text
dist/
```
If the script has a different filename, replace scraper.py in the command.

# Future Improvements

## Possible future enhancements include:

Login/session management
Configurable retry count
Detailed application log file
Custom output directory selection
Pause and resume functionality
Download history
More TradingView intervals
Automatic data validation
Excel output option
Improved GUI design
Multi-symbol parallel processing

# Author

Satish Yadav

GitHub: https://github.com/Satishji111

Repository: https://github.com/Satishji111/Trading-view-scrapper
