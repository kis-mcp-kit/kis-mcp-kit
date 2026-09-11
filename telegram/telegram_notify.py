# -*- coding: utf-8 -*-
"""Send a text message to Telegram.

Reads bot_token and chat_id from telegram_config.txt (JSON) next to this file.
Environment variables TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID take precedence.

Usage:
    python telegram_notify.py "your message"
    echo "your message" | python telegram_notify.py

From other code:
    from telegram_notify import send
    send("filled: 005930 x73 @259500")
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "telegram_config.txt")
API_URL = "https://api.telegram.org/bot{token}/sendMessage"
TIMEOUT = 10


def load_config():
    """Return (bot_token, chat_id). Raises RuntimeError if either is missing."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not (token and chat_id):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            raise RuntimeError("config file not found: %s" % CONFIG_PATH)
        except ValueError as exc:
            raise RuntimeError("config file is not valid JSON: %s (%s)" % (CONFIG_PATH, exc))

        token = token or str(cfg.get("bot_token", "")).strip()
        chat_id = chat_id or str(cfg.get("chat_id", "")).strip()

    # A placeholder left in the template is not a real value.
    if token.startswith("<"):
        token = ""
    if chat_id.startswith("<"):
        chat_id = ""

    missing = [n for n, v in (("bot_token", token), ("chat_id", chat_id)) if not v]
    if missing:
        raise RuntimeError("missing %s in %s" % (" and ".join(missing), CONFIG_PATH))

    return token, chat_id


def send(text, silent=False):
    """Send text as-is. Returns True on success, raises RuntimeError otherwise."""
    text = str(text)
    if not text.strip():
        raise ValueError("message is empty")

    token, chat_id = load_config()
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": "true" if silent else "false",
        }
    ).encode("utf-8")

    request = urllib.request.Request(API_URL.format(token=token), data=payload)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("telegram api error %s: %s" % (exc.code, exc.read().decode("utf-8", "replace")))
    except urllib.error.URLError as exc:
        raise RuntimeError("telegram connection failed: %s" % (exc.reason,))

    if not result.get("ok"):
        raise RuntimeError("telegram rejected the message: %s" % result)
    return True


def main(argv):
    text = " ".join(argv[1:]) if len(argv) > 1 else sys.stdin.read()
    try:
        send(text)
    except (RuntimeError, ValueError) as exc:
        sys.stderr.write("%s\n" % exc)
        return 1
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
