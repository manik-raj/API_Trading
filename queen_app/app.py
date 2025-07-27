# app.py

import threading
from flask import Flask
from pawn_handler import PawnHandler
from trader_logic import process_position_data
from telegram_bot import run_bot

# 🚀 Flask app for Queen
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health_check():
    return {"status": "Queen is alive"}

def start_flask():
    flask_app.run(host="0.0.0.0", port=5000)

def start_pawn_watcher():
    handler = PawnHandler()
    handler.run_cycle(callback=process_position_data)

if __name__ == "__main__":
    # 🔁 Start Pawn polling
    threading.Thread(target=start_pawn_watcher, daemon=True).start()

    # 🌐 Start Flask
    threading.Thread(target=start_flask, daemon=True).start()

    # 🤖 Start Telegram bot (blocking)
    run_bot()
