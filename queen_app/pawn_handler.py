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
            print("caught exception in get_position_data", flush=True)
            print(str(e), flush=True)
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
            try:
                result = self.get_position_data()
                print(f"[PAWN CHECK] -> {result['pawn_url']}", flush=True)
                if "response" in result:
                    print(f"[PAWN CHECK] -> {result['response']}", flush=True)
                elif "error" in result:
                    print(f"[PAWN ERROR] -> {result['error']}", flush=True)
                
                # pass the response to some handler
                if callback:
                    callback(result)
            except Exception as e:
                print(f"[PAWN EXCEPTION] -> {str(e)}", flush=True)
            wait_time = random.randint(8, 12)
            time.sleep(wait_time)
