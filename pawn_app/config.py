# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PAWN_API_KEY")  
MONITOR_BASE_URL = os.getenv("MONITOR_ENDPOINT")  
