# pawn_handler.py

import time
import random
import requests
from config import PAWN_ENDPOINTS, PAWN_API_KEY, TRADER_UID

class PawnHandler:
    def __init__(self):
        self.pawns = PAWN_ENDPOINTS
        self.current_index = 0

    def get_next_pawn_url(self):
        url = self.pawns[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.pawns)
        return url

    def get_position_data(self):
        url = self.get_next_pawn_url()
        payload = { "traderUid": TRADER_UID }
        headers = { "Authorization": f"Bearer {PAWN_API_KEY}" }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return {
                "pawn_url": url,
                "status_code": response.status_code,
                "response": response.json()
            }
        except Exception as e:
            return {
                "pawn_url": url,
                "status_code": None,
                "error": str(e)
            }

    def run_cycle(self, callback=None):
        """
        Loop through pawns forever. Optional callback to handle the response.
        """
        while True:
            result = self.get_position_data()
            print(f"[PAWN CHECK] -> {result['pawn_url']}")
            print(f"[PAWN CHECK] -> {result['response']}")
            
            # pass the response to some handler
            if callback:
                callback(result)

            wait_time = random.randint(8, 12)
            time.sleep(wait_time)
