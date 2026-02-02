from flask import Flask, request, redirect, abort
import time
import os

app = Flask(__name__)

TARGET_URL = "https://forms.gle/8ay3uHDVqMKmQr72A"

valid_tokens = {}

@app.route("/")
def home():
    return "Dynamic QR server is running"

@app.route("/qr")
def qr_redirect():
    token = request.args.get("token")

    if not token:
        return "Missing token", 403

    exp = valid_tokens.get(token)
    if exp is None:
        return "Token not found (server may have restarted)", 403

    if time.time() > exp:
        return "Token expired", 403

    return redirect(TARGET_URL)


@app.route("/register")
def register_token():
    token = request.args.get("token")
    if not token:
        return "Missing token", 400

    valid_tokens[token] = time.time() + 15
    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
