import decimal
import json

import websocket

from utils import calculate_ma, send_telegram_message

# Binance WebSocket URL
socket_url = "wss://stream.binance.com:9443/ws"

# Binance API URL
api_url = "https://api.binance.com/api/v3"

# Telegram API URL and bot token
telegram_api_url = "https://api.telegram.org/bot"
telegram_bot_token = '6247565543:AAEOCrSc0GCedDXHlj5LF8fTY8z-3ayvRh4'
telegram_chat_id = '-1001962594807'

# Symbol, period, interval, and limit

S = "BNBUSDT"  # Trading symbol, e.g., "BNBUSDT"
N = 8  # Number of candles for moving average
T = 30  # Candle interval in minutes
L = 3  # Number of candles required to trigger a notification

# Initialize variables
close_prices = []
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
    json_message = json.loads(message)
    if "k" in json_message:
        candle_data = json_message["k"]
        close_price = decimal.Decimal(candle_data["c"])
        close_prices.append(close_price)

        if len(close_prices) > N:
            close_prices.pop(0)

        ma_value = calculate_ma(close_prices)
        print(f"Close price: {close_price}, MA: {ma_value}")

        if close_price > ma_value:
            candle_count += 1
        else:
            candle_count = 0

        if candle_count >= L:
            notification_message = f"Close price intercrossed MA for {S}! Candle count: {candle_count}"
            send_telegram_message(notification_message, telegram_api_url, telegram_bot_token, telegram_chat_id)


# WebSocket on_close event handler
def on_close(ws):
    print("WebSocket connection closed.")


if __name__ == "__main__":
    websocket.enableTrace(False) # Enable this to see WebSocket debug messages
    ws = websocket.WebSocketApp(socket_url, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
