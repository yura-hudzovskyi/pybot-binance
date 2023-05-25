import requests


def calculate_ma(prices):
    return sum(prices) / len(prices)


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

