# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Trading Configs
TRADER_UID = os.getenv("TRADER_UID")
TRADER_ACC_BALANCE = float(os.getenv("TRADER_ACC_BALANCE", "0"))
MY_ACC_BALANCE = float(os.getenv("MY_ACC_BALANCE", "0"))

# Pawn Endpoints
PAWN_1 = os.getenv("PAWN_1")
PAWN_2 = os.getenv("PAWN_2")
PAWN_3 = os.getenv("PAWN_3")
PAWN_ENDPOINTS = [PAWN_1, PAWN_2, PAWN_3]

# Shared Auth
PAWN_API_KEY = os.getenv("PAWN_API_KEY")

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = [chat_id.strip() for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if chat_id.strip()]

BITUNIX_API_KEY = os.getenv("BITUNIX_API_KEY")
BITUNIX_API_SECRET = os.getenv("BITUNIX_API_SECRET")
