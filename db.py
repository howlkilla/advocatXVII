import sqlite3
from datetime import datetime

def init():
    conn = sqlite3.connect("justice.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ds_msg_id TEXT,
        sender TEXT,
        content TEXT,
        status TEXT,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

def add_call(msg_id, sender, content):
    conn = sqlite3.connect("justice.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO calls (ds_msg_id, sender, content, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                (str(msg_id), sender, content, "Ожидание", datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()

def update_status(msg_id, status):
    conn = sqlite3.connect("justice.db")
    cur = conn.cursor()
    cur.execute("UPDATE calls SET status = ? WHERE ds_msg_id = ?", (status, str(msg_id)))
    conn.commit()
    conn.close()

def get_history(limit=10):
    conn = sqlite3.connect("justice.db")
    cur = conn.cursor()
    cur.execute("SELECT sender, status, timestamp FROM calls ORDER BY id DESC LIMIT ?", (limit,))
    res = cur.fetchall()
    conn.close()
    return res