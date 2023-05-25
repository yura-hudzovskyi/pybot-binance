import decimal
import json

import requests



def calculate_ma(symbol, interval, limit, client):
    klines = client.klines(symbol=symbol, interval=interval)
    closing_prices = [float(kline[4]) for kline in klines]
    if len(closing_prices) < limit:
        return None

    ma = sum(closing_prices[-limit:]) / limit

    return ma


# Function to send a message via Telegram
def send_telegram_message(message, telegram_api_url, telegram_bot_token, telegram_chat_id):
    url = f"{telegram_api_url}{telegram_bot_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message,
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send Telegram message. Error: {response.text}")


def get_candles(symbol, interval, limit, close_prices, api_url):
    endpoint = f"{api_url}/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        candles = json.loads(response.text)
        data = [decimal.Decimal(candle[4]) for candle in candles]  # Get close prices from candles
        close_prices.extend(data)
    else:
        print("Failed to retrieve candles from Binance API.")
        return []

