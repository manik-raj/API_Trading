# auth.py
from flask import request, jsonify
from config import API_KEY

def queen_only(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_KEY}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper
