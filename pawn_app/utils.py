# utils.py
import requests
from datetime import datetime

def fetch_positions(final_url):
    try:
        response = requests.get(final_url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Bitunix API error", "status_code": response.status_code, "body": response.json()}
        
        json_data = response.json()
        if not json_data.get("data"):
            return {"data": None}
        
        results = []
        for item in json_data["data"]:
            try:
                entry_price = float(item["openVal"]) / float(item["amount"])
                formatted_ctime = datetime.strptime(item["ctime"], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S, %d:%m:%Y")
                results.append({
                    "positionId": item["positionId"],
                    "ctime": formatted_ctime,
                    "symbol": item["symbol"],
                    "type": item["type"],
                    "side": item["side"],
                    "leverage": item["leverage"],
                    "amount": item["amount"],
                    "marginAmount": item["marginAmount"],
                    "entry_price": round(entry_price, 6),
                    "positionMode": item["positionMode"],
                })
            except Exception as e:
                continue
        return {"data": results}
    
    except Exception as e:
        return {"error": str(e)}
