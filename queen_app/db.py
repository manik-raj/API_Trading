# db.py

import sqlite3
import os
from datetime import datetime

DB_PATH = "queen.db"

# --------------------------- 📡 COPY TRADER TRACKING ---------------------------

class PositionDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_position_table()

    def create_position_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                positionId TEXT PRIMARY KEY,
                symbol TEXT,
                ctime TEXT,
                type INTEGER,
                side INTEGER,
                leverage INTEGER,
                amount REAL,
                marginAmount REAL,
                entry_price REAL,
                positionMode INTEGER
            )
        ''')
        self.conn.commit()

    def get_position(self, position_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE positionId = ?", (position_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "positionId": row[0],
            "symbol": row[1],
            "ctime": row[2],
            "type": row[3],
            "side": row[4],
            "leverage": row[5],
            "amount": row[6],
            "marginAmount": row[7],
            "entry_price": row[8],
            "positionMode": row[9],
        }

    def save_position(self, pos):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO positions (positionId, symbol, ctime, type, side, leverage, amount, marginAmount, entry_price, positionMode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(positionId) DO UPDATE SET
                symbol=excluded.symbol,
                ctime=excluded.ctime,
                type=excluded.type,
                side=excluded.side,
                leverage=excluded.leverage,
                amount=excluded.amount,
                marginAmount=excluded.marginAmount,
                entry_price=excluded.entry_price,
                positionMode=excluded.positionMode
        ''', (
            pos["positionId"],
            pos["symbol"],
            pos["ctime"],
            pos["type"],
            pos["side"],
            pos["leverage"],
            pos["amount"],
            pos["marginAmount"],
            pos["entry_price"],
            pos["positionMode"]
        ))
        self.conn.commit()

    def remove_closed_positions(self, current_ids):
        cursor = self.conn.cursor()
        cursor.execute("SELECT positionId FROM positions")
        all_ids = [row[0] for row in cursor.fetchall()]
        for pid in all_ids:
            if pid not in current_ids:
                print(f"❌ Position closed: {pid}")
                cursor.execute("DELETE FROM positions WHERE positionId = ?", (pid,))
        self.conn.commit()

    def get_all_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT positionId FROM positions")
        return [row[0] for row in cursor.fetchall()]
    
    def remove_copy_position_id(self, copy_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM positions WHERE positionId = ?", (copy_id,))
        self.conn.commit()


# --------------------------- 🔗 MAPPING COPY ↔ MY POSITIONS ---------------------------

class PositionMapDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_map_table()

    def create_map_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_map (
                copy_position_id TEXT PRIMARY KEY,
                my_position_id TEXT,
                symbol TEXT,
                side TEXT,
                leverage INTEGER,
                qty REAL,
                opened_at TEXT
            )
        ''')
        self.conn.commit()

    def add_mapping(self, copy_id, my_id, symbol, side, leverage, qty):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO position_map
            (copy_position_id, my_position_id, symbol, side, leverage, qty, opened_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (copy_id, my_id, symbol, side, leverage, qty, datetime.utcnow().isoformat()))
        self.conn.commit()

    def get_my_position_id(self, copy_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT my_position_id FROM position_map WHERE copy_position_id = ?", (copy_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def remove_mapping(self, copy_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM position_map WHERE copy_position_id = ?", (copy_id,))
        self.conn.commit()

    def get_all_mappings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM position_map")
        return cursor.fetchall()
