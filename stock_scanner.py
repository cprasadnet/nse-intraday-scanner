# stock_scanner.py
import yfinance as yf
import requests
import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

STOCKS = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS"]

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

RISK_REWARD = 4

for symbol in STOCKS:
    try:
        df = yf.download(tickers=symbol, interval="1m", period="1d", progress=False)
        if len(df) < 6:
            continue

        latest = df.iloc[-1]
        volume = latest["Volume"]
        close = latest["Close"]
        low = latest["Low"]

        hist = yf.download(tickers=symbol, period="5d", interval="1d", progress=False)
        avg_vol = hist["Volume"].mean()
        vol_threshold = 10 * (avg_vol / 375)
        value_traded = volume * close

        if volume >= vol_threshold or value_traded >= 4e7:
            entry = close
            stoploss = low
            risk = entry - stoploss
            target = entry + risk * RISK_REWARD

            msg = (
                f"📈 ENTRY SIGNAL for {symbol}\n"
                f"Price: ₹{entry:.2f}\n"
                f"Stoploss: ₹{stoploss:.2f}\n"
                f"Target (1:4): ₹{target:.2f}\n"
                f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            send_alert(msg)

    except Exception as e:
        send_alert(f"⚠️ Error in {symbol}: {e}")
