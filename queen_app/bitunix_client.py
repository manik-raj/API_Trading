# bitunix_client.py

import time
import json
import hashlib
import random
import string
import requests
from collections import OrderedDict
from config import BITUNIX_API_KEY, BITUNIX_API_SECRET

BASE_URL = "https://fapi.bitunix.com"

# === 🔐 Helpers ===

def generate_nonce(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_timestamp():
    return time.strftime("%Y%m%d%H%M%S", time.gmtime())  # yyyyMMddHHmmss

def generate_signature(nonce, timestamp, api_key, query_str, body_str):
    digest_input = nonce + timestamp + api_key + query_str + body_str
    digest = hashlib.sha256(digest_input.encode('utf-8')).hexdigest()
    sign_input = digest + BITUNIX_API_SECRET
    return hashlib.sha256(sign_input.encode('utf-8')).hexdigest()

def signed_request(method, endpoint, params=None, body=None):
    url = BASE_URL + endpoint
    api_key = BITUNIX_API_KEY
    nonce = generate_nonce()
    timestamp = get_timestamp()

    query_str = ""
    if method == "GET" and params:
        query_str = ''.join([f"{k}{v}" for k, v in sorted(params.items())])

    body_str = json.dumps(body, separators=(',', ':'), ensure_ascii=False) if body else ""

    sign = generate_signature(nonce, timestamp, api_key, query_str, body_str)

    headers = {
        "api-key": api_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
        "language": "en-US",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            res = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            res = requests.post(url, headers=headers, data=body_str, timeout=10)
            print("***************", flush=True)
            print("after request:", flush=True)
            print(res.status_code, flush=True)
            print(res.json(), flush=True)
            print("***************", flush=True)
        return res.status_code, res.json()
    except Exception as e:
        print("***************", flush=True)
        print("Exception in singed request",str(e), flush=True)
        print("***************", flush=True)
        return 500, {"error": str(e)}

# === 🔁 Trade & Position Functions ===

def get_pending_positions(symbol=None):
    params = {"symbol": symbol} if symbol else {}
    return signed_request("GET", "/api/v1/futures/position/get_pending_positions", params=params)

def place_order(symbol, qty, side, trade_side, order_type="MARKET", price=None,
                tp_price=None, sl_price=None, client_id=None, reduce_only=False):
    print("***************", flush=True)
    print("Entered Place order", flush=True)
    print("***************", flush=True)
    body = OrderedDict([
        ("symbol", symbol),
        ("qty", str(qty)),
        ("side", side),
        ("tradeSide", trade_side),
        ("orderType", order_type),
        ("reduceOnly", reduce_only)
    ])
    if price:
        body["price"] = str(price)
        body["effect"] = "GTC"
    if client_id:
        body["clientId"] = client_id
    if tp_price:
        body.update({
            "tpPrice": str(tp_price),
            "tpStopType": "MARK_PRICE",
            "tpOrderType": "MARKET"
        })
    if sl_price:
        body.update({
            "slPrice": str(sl_price),
            "slStopType": "MARK_PRICE",
            "slOrderType": "MARKET"
        })

    return signed_request("POST", "/api/v1/futures/trade/place_order", body=body)

def flash_close_position(position_id):

    print("***************", flush=True)
    print("Entered flash close", flush=True)
    print("***************", flush=True)
    body = {"positionId": position_id}
    return signed_request("POST", "/api/v1/futures/trade/flash_close_position", body=body)

# === ⚙️ Margin & Leverage ===

def get_margin_mode(symbol):
    params = {"symbol": symbol, "marginCoin": "USDT"}
    status, data = signed_request("GET", "/api/v1/futures/account/get_leverage_margin_mode", params=params)
    if status == 200 and data["code"] == 0:
        return data["data"].get("marginMode", None)
    return None

def change_margin_mode(symbol, mode="CROSS"):
    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "marginMode": mode
    }
    return signed_request("POST", "/api/v1/futures/account/change_margin_mode", body=body)

def change_leverage(symbol, leverage):
    body = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "leverage": leverage
    }
    return signed_request("POST", "/api/v1/futures/account/change_leverage", body=body)
