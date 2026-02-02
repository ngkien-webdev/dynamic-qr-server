from flask import Flask, request, redirect
import time
import os
import sqlite3

app = Flask(__name__)

TARGET_URL = "https://forms.gle/8ay3uHDVqMKmQr72A"
DB_FILE = "tokens.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            exp REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Dynamic QR server (sqlite) running"

@app.route("/register")
def register_token():
    token = request.args.get("token")
    if not token:
        return "missing token", 400

    exp = time.time() + 15

    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO tokens(token, exp) VALUES(?, ?)",
        (token, exp)
    )
    conn.commit()
    conn.close()

    return "ok"

@app.route("/qr")
def qr_redirect():
    token = request.args.get("token")
    if not token:
        return "missing token", 403

    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT exp FROM tokens WHERE token=?",
        (token,)
    )
    row = c.fetchone()
    conn.close()

    if row is None:
        return "token not found", 403

    if time.time() > row[0]:
        return "token expired", 403

    return redirect(TARGET_URL)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
