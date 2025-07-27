import requests
import time
import os

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS

# Telegram API base URL
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# In-memory config mirror (can update via commands)
state = {
    "TRADER_UID": os.getenv("TRADER_UID"),
    "TRADER_ACC_BALANCE": float(os.getenv("TRADER_ACC_BALANCE", "0")),
}

# 🔔 Notify all chat IDs
def send_notification(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": message}, timeout=5)
        except Exception as e:
            print(f"Telegram send error: {e}")

# Handle incoming updates
def handle_update(update):
    message = update.get('message')
    if not message or 'text' not in message:
        return

    text = message['text']
    chat_id = message['chat']['id']

    if text.startswith('/getM'):
        response = f"📊 Trader Balance (M): {state['TRADER_ACC_BALANCE']} USDT"

    elif text.startswith('/getT'):
        response = f"🆔 Trader UID (T): {state['TRADER_UID']}"

    elif text.startswith('/updateM'):
        try:
            amount = float(text.split()[1])
            state['TRADER_ACC_BALANCE'] = amount
            response = f"✅ Updated Trader Balance to {amount} USDT"
        except:
            response = "❌ Usage: /updateM <amount>"

    elif text.startswith('/updateT'):
        try:
            uid = text.split()[1]
            state['TRADER_UID'] = uid
            response = f"✅ Updated Trader UID to {uid}"
        except:
            response = "❌ Usage: /updateT <trader_uid>"

    else:
        response = "⚠️ Unknown command."

    # Send reply
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": response}, timeout=5)

# Long polling loop
def run_bot():
    print("🤖 Telegram bot is running (without external lib)...")
    offset = None

    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={"timeout": 100, "offset": offset}, timeout=120)
            updates = resp.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                handle_update(update)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


