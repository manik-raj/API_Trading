# app.py
from flask import Flask, request, jsonify
from config import MONITOR_BASE_URL
import sys
from auth import queen_only
from utils import fetch_positions

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return {"status": "Pawn is alive"}

@app.route("/monitor/", methods=["POST"])
@queen_only
def monitor():
    data = request.get_json()
    trader_uid = data.get("traderUid")

    if not trader_uid:
        return jsonify({"error": "Missing traderUid"}), 400

    final_url = f"{MONITOR_BASE_URL}{trader_uid}"
    result = fetch_positions(final_url)
    return jsonify(result)

# if __name__ == "__main__":
#     port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
#     app.run(port=port,debug=True)
