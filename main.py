import decimal
import json
import os

from dotenv import load_dotenv
import websocket
from binance.spot import Spot as Client

from utils import calculate_ma, send_telegram_message, get_candles

load_dotenv()

# Binance WebSocket URL
socket_url = "wss://stream.binance.com:9443/ws"

# Binance API URL
api_url = "https://api.binance.com/api/v3"

# Telegram API URL and bot token
telegram_api_url = "https://api.telegram.org/bot"
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

Client = Client()

# Symbol, period, interval, and limit

S = "BNBUSDT"  # Trading symbol, e.g., "BNBUSDT"
N = 7  # Number of candles for moving average
T = 1  # Candle interval in minutes
L = 3  # Number of candles required to trigger a notification

# Initialize variables
close_prices = []
last_kline_time = None
ma_value = 0
candle_count = 0


def on_open(ws):
    print("WebSocket connection opened.")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [f"{S.lower()}@kline_{T}m"],
        "id": 1,
    }
    ws.send(json.dumps(subscribe_message))


def on_message(ws, message):
    global candle_count
    global last_kline_time

    json_message = json.loads(message)
    if "k" in json_message:
        candle_data = json_message["k"]
        print(candle_data["T"])
        print(last_kline_time)

        if last_kline_time == candle_data["T"]:
            print("Duplicate kline received, ignoring.")
            return

        else:
            last_kline_time = candle_data["T"]

            close_price = decimal.Decimal(candle_data["c"])
            close_prices.append(close_price)
            print(close_prices, "INSIDE")

            if len(close_prices) > N:
                close_prices.pop(0)

            ma_value = calculate_ma(symbol=S, interval=f"{T}m", limit=N, client=Client)
            print(f"Close price: {close_price}, MA: {ma_value}")

            if close_price > ma_value:
                candle_count += 1
            else:
                candle_count = 0

            if candle_count >= L:
                message = f"Close price {close_price} is above MA {ma_value} for {candle_count} candles."
                send_telegram_message(message, telegram_api_url, telegram_bot_token, telegram_chat_id)
                candle_count = 0


# WebSocket on_close event handler
def on_close(ws):
    print("WebSocket connection closed.")


if __name__ == "__main__":
    websocket.enableTrace(True) # Enable this to see WebSocket debug messages
    print(close_prices, "before")
    get_candles(S, f"{T}m", N, close_prices, api_url)
    print(close_prices, "after")
    ws = websocket.WebSocketApp(socket_url, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
