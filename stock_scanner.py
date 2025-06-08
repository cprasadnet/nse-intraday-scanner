# stock_scanner.py
import yfinance as yf
import requests
import datetime
import os

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # From Render Environment Variable
CHAT_ID = os.getenv("CHAT_ID")      # From Render Environment Variable

# You can change or add more symbols from NSE
STOCKS = ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "INFY.NS"]

RISK_REWARD = 4  # 1:4 Risk-Reward Ratio


def send_alert(message):
    """Send Telegram message via bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)


def scan_stock(symbol):
    try:
        # 1-minute intraday data
        df = yf.download(tickers=symbol, interval="1m", period="1d", progress=False, auto_adjust=False)

        if len(df) < 6:
            return

        latest = df.iloc[-1]
        volume = float(latest["Volume"])
        close = float(latest["Close"])
        low = float(latest["Low"])

        # Get average daily volume over past 5 days
        hist = yf.download(tickers=symbol, interval="1d", period="5d", progress=False)
        avg_volume = hist["Volume"].mean()

        # Conditions
        vol_threshold = 10 * (avg_volume / 375)
        value_traded = volume * close

        if volume >= vol_threshold or value_traded >= 4e7:
            entry = close
            stoploss = low
            risk = entry - stoploss
            if risk <= 0:
                return
            target = entry + RISK_REWARD * risk

            msg = (
                f"📢 *ENTRY SIGNAL* for `{symbol}`\n"
                f"💰 *Entry*: ₹{entry:.2f}\n"
                f"🛑 *Stoploss*: ₹{stoploss:.2f}\n"
                f"🎯 *Target* (1:4): ₹{target:.2f}\n"
                f"🕒 Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            send_alert(msg)

    except Exception as e:
        send_alert(f"⚠️ Error in {symbol}: {e}")


# === Run Scanner ===
for stock in STOCKS:
    scan_stock(stock)
