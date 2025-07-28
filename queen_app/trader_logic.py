# trader_logic.py
import time
from db import PositionDB, PositionMapDB
from bitunix_client import (
    get_pending_positions,
    place_order,
    flash_close_position,
    get_margin_mode,
    change_margin_mode,
    change_leverage
)
from config import TRADER_ACC_BALANCE, MY_ACC_BALANCE
from telegram_bot import send_notification

copy_db = PositionDB()
map_db = PositionMapDB()

def process_position_data(response):
    if response.get("status_code") != 200:
        send_notification(f"❗ Error from Pawn: {response.get('response') or response.get('error')}")
        return

    new_data = response["response"].get("data")
    if new_data is None:
        #send_notification("ℹ️ No open positions from copy trader.")
        return

    current_copy_ids = []

    for pos in new_data:
        copy_id = pos["positionId"]
        symbol = pos["symbol"]
        side = pos["side"]
        leverage = pos["leverage"]
        amount = float(pos["amount"])
        margin = float(pos["marginAmount"])

        current_copy_ids.append(copy_id)

        previous = copy_db.get_position(copy_id)
        my_qty = (amount * MY_ACC_BALANCE) / TRADER_ACC_BALANCE

        if not previous:
            # ✅ New position
            print("Entered new position", flush=True)
            status, pending = get_pending_positions(symbol)
            if not pending["data"]:
                current_mode = get_margin_mode(symbol)
                if current_mode != "CROSS":
                    change_margin_mode(symbol, "CROSS")

            side_str = "BUY" if side == 2 else "SELL"
            trade_side = "OPEN"
            result = place_order(symbol, qty=my_qty, side=side_str, trade_side=trade_side)

            if result[0] == 200 and result[1]["code"] == 0:
                my_id = extract_my_position_id(symbol, side_str)
                if my_id:
                    map_db.add_mapping(copy_id, my_id, symbol, side_str, leverage, my_qty)
                send_notification(f"✅ New position: {symbol} {side_str} {round(my_qty, 4)}x{leverage}")
                copy_db.save_position(pos)  # Only save if opened successfully
            else:
                send_notification(f"❌ Failed to open position: {result[1]}")
        else:
            # 🧠 Compare for changes
            old_amount = float(previous["amount"])
            old_leverage = int(previous["leverage"])
            delta = round(amount - old_amount, 6)
            changed = False

            if delta != 0:
                qty_diff = (abs(delta) * MY_ACC_BALANCE) / TRADER_ACC_BALANCE
                #side_str = "BUY" if side == 2 else "SELL"
                trade_side = "OPEN"
                reduce = delta < 0
                original_side_str = "BUY" if side == 2 else "SELL"
                side_str = (
                    "SELL" if reduce and original_side_str == "BUY"
                    else "BUY" if reduce and original_side_str == "SELL"
                    else original_side_str
                )
                print("Entered change position ", reduce)
                result = place_order(
                    symbol, qty=qty_diff, side=side_str, trade_side=trade_side, reduce_only=reduce
                )
                action = "Increase" if delta > 0 else "Reduce"
                send_notification(f"🔁 {action} {symbol} {side_str} by {round(qty_diff, 4)}")
                changed = True

            if leverage != old_leverage:
                status, res = change_leverage(symbol, leverage)
                if status == 200 and res["code"] == 0:
                    send_notification(f"⚙️ Changed leverage on {symbol} to {leverage}x")
                else:
                    send_notification(f"❌ Failed to change leverage: {res}")
                changed = True

            if changed:
                copy_db.save_position(pos)

    # 🔴 Handle closed copy positions
    handle_closed_positions(current_copy_ids)

def handle_closed_positions(current_ids):
    all_tracked = copy_db.get_all_ids()
    for copy_id in all_tracked:
        if copy_id not in current_ids:
            my_id = map_db.get_my_position_id(copy_id)
            if my_id:
                result = flash_close_position(my_id)
                if result[0] == 200 and result[1]["code"] == 0:
                    send_notification(f"🔻 Closed position {copy_id} → mine: {my_id}")
                else:
                    send_notification(f"⚠️ Failed to close position {copy_id} → {result[1]}")
                map_db.remove_mapping(copy_id)
                copy_db.remove_copy_position_id(copy_id)  # Clean up

def extract_my_position_id(symbol, side):
    time.sleep(1) 
    status, data = get_pending_positions(symbol)
    if status == 200 and data["code"] == 0:
        for pos in data["data"]:
            if pos["symbol"] == symbol and pos["side"] == side:
                return pos["positionId"]
    return None
