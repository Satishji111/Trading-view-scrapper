# 📈 TradingView Scraper (OHLCV Data Extractor)

A Python-based tool to **extract OHLCV (Open, High, Low, Close, Volume) market data** from TradingView for **any market and timeframe**. This project is designed for traders, analysts, and data scientists who need structured market data for analysis, backtesting, and research.

---

## 📌 Project Overview

TradingView provides rich market data but does not allow easy bulk export for free users. This tool bridges that gap by enabling:

* Automated OHLCV data extraction
* Support for multiple exchanges
* Flexible timeframe selection
* Clean, analysis-ready output

This repository demonstrates **financial data engineering skills** combined with **Python automation**.

---

## 🎯 Key Features

* 📊 Extract OHLCV data (Open, High, Low, Close, Volume)
* 🌍 Works with **any TradingView-supported market**
* ⏱️ Multiple timeframes (Intraday / Daily / Weekly / Monthly)
* 🧹 Clean and structured output (CSV / DataFrame ready)
* 🔁 Can be integrated into trading strategies & ML pipelines

---

## 🗂️ Project Structure

```bash
Trading-view-scrapper/
│
├── src/
│   ├── tradingview_scraper.py   # Core scraping & data extraction logic
│   ├── utils.py                 # Helper functions
│   └── config.py                # Market, symbol & timeframe configuration
│
├── output/
│   └── ohlcv_data.csv            # Extracted OHLCV data
│
├── requirements.txt
├── README.md
└── main.py                       # Script entry point
```

*(Structure may vary slightly based on implementation)*

---

## ⚙️ Technologies Used

* **Python** 🐍
* Pandas
* Requests / WebSocket / Selenium *(as applicable)*
* TradingView data source

---

## ▶️ How It Works

1. User provides:

   * Market / Exchange
   * Symbol (e.g. NSE:RELIANCE, NASDAQ:AAPL, BTCUSDT)
   * Timeframe

2. Script connects to TradingView

3. OHLCV data is fetched programmatically

4. Data is saved in a structured format for analysis

---

## ▶️ How to Run the Project

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Satishji111/Trading-view-scrapper.git
cd Trading-view-scrapper
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Market & Symbol

Update symbol, exchange, and timeframe inside the configuration file or script.

### 4️⃣ Run the Scraper

```bash
python main.py
```

---

## 📊 Sample Output

| Date       | Open | High | Low  | Close | Volume    |
| ---------- | ---- | ---- | ---- | ----- | --------- |
| 2024-01-01 | 2450 | 2480 | 2430 | 2470  | 1,250,000 |

Output can be directly used for:

* Technical analysis
* Backtesting strategies
* Machine learning models

---

## 📌 Use Cases

* Algorithmic trading research
* Strategy backtesting
* Market data collection
* Quantitative analysis
* ML-based price prediction

---

## ⚠️ Disclaimer

This project is created **strictly for educational and research purposes**. Please ensure compliance with TradingView’s terms of service before using this tool for commercial purposes.

---

## 🚀 Future Enhancements

* Add real-time streaming support
* Add automatic retries & error handling
* Support batch symbol extraction
* Integrate with backtesting frameworks
* Add Docker support

---

## 👨‍💻 Author

**Satish Yadav**
Senior Data Research Analyst
📈 Quantitative Analysis | Trading Automation | Python | SQL

🔗 GitHub: [https://github.com/Satishji111](https://github.com/Satishji111)

---

## ⭐ Support

If you find this project useful, please **star ⭐ the repository**. It helps others discover the project and supports further development.
