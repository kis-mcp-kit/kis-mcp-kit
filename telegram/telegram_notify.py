# -*- coding: utf-8 -*-
"""Send a text message to Telegram.

Reads settings from telegram_config.txt (JSON) next to this file:

    bot_token     required -- from @BotFather
    bot_username  the bot you created, e.g. "my_assistant_bot"
    chat_id       leave empty; filled in automatically on first send

You only fill in the two bot fields. The chat_id -- who the bot sends to --
is discovered from whoever has sent the bot a message, then cached.

Environment variables TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID take precedence.

Usage:
    python telegram_notify.py "your message"
    echo "your message" | python telegram_notify.py
    python telegram_notify.py --resolve     # look up chat_id and save it

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
API_URL = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 10

PLACEHOLDERS = ("", "your_token", "your_bot_username", "your_chat_id",
                "token", "bot_username", "chat_id")


def _is_placeholder(value):
    """True if the value is still the template's filler rather than a real one.

    Without this an unedited config reaches Telegram and comes back as a bare
    404, which reads like a bug instead of "you have not filled this in yet".
    """
    return value.strip().strip("<>").strip(".").strip().lower() in PLACEHOLDERS


def _call(token, method, params=None):
    """Call a Bot API method. Returns the `result` field."""
    data = urllib.parse.urlencode(params).encode("utf-8") if params else None
    request = urllib.request.Request(API_URL.format(token=token, method=method), data=data)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        if exc.code == 404:
            raise RuntimeError("telegram api error 404: bot_token looks wrong -- check %s" % CONFIG_PATH)
        raise RuntimeError("telegram api error %s: %s" % (exc.code, body))
    except urllib.error.URLError as exc:
        raise RuntimeError("telegram connection failed: %s" % (exc.reason,))

    if not payload.get("ok"):
        raise RuntimeError("telegram rejected the request: %s" % payload)
    return payload.get("result")


def _read_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError("config file not found: %s" % CONFIG_PATH)
    except ValueError as exc:
        raise RuntimeError("config file is not valid JSON: %s (%s)" % (CONFIG_PATH, exc))


def _write_chat_id(chat_id):
    """Persist a resolved chat_id, leaving every other key untouched."""
    cfg = _read_config()
    cfg["chat_id"] = str(chat_id)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _describe(chat):
    name = chat.get("title") or " ".join(
        filter(None, [chat.get("first_name"), chat.get("last_name")])
    ) or "(no name)"
    handle = chat.get("username")
    return "%s%s" % (name, " (@%s)" % handle if handle else "")


def check_bot(token, bot_username=""):
    """Confirm the token works, and that it belongs to the expected bot."""
    bot = _call(token, "getMe")
    actual = str(bot.get("username", ""))
    wanted = bot_username.strip().lstrip("@")
    if wanted and not _is_placeholder(wanted) and wanted.lower() != actual.lower():
        raise RuntimeError(
            "bot_token belongs to @%s, but bot_username says @%s -- check %s"
            % (actual, wanted, CONFIG_PATH)
        )
    return bot


def resolve_chat_id(token):
    """Find who the bot should send to, from messages the bot has received.

    A bot cannot look up a person and start a conversation -- Telegram only
    lets it reply to someone who wrote first. So the recipient is whoever has
    already messaged this bot, which is why setup asks you to send /start.

    Returns (chat_id, chat_dict).
    """
    chats = {}
    for update in _call(token, "getUpdates") or []:
        message = (
            update.get("message")
            or update.get("edited_message")
            or update.get("channel_post")
            or {}
        )
        chat = message.get("chat") or {}
        if chat.get("id"):
            chats[str(chat["id"])] = chat

    if not chats:
        raise RuntimeError(
            "nobody has messaged this bot yet -- open it in Telegram, send /start, then retry"
        )

    if len(chats) == 1:
        chat_id = next(iter(chats))
        return chat_id, chats[chat_id]

    listed = ", ".join("%s -> %s" % (c, _describe(v)) for c, v in chats.items())
    raise RuntimeError(
        "several chats have messaged this bot -- put the one you want in chat_id "
        "in %s. Candidates: %s" % (CONFIG_PATH, listed)
    )


def load_config(auto_resolve=True):
    """Return (bot_token, chat_id), resolving and caching chat_id if needed."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    bot_username = ""

    if not (token and chat_id):
        cfg = _read_config()
        token = token or str(cfg.get("bot_token", "")).strip()
        chat_id = chat_id or str(cfg.get("chat_id", "")).strip()
        bot_username = str(cfg.get("bot_username", "")).strip()

    if _is_placeholder(token):
        raise RuntimeError("set bot_token in %s -- see README.md" % CONFIG_PATH)

    if _is_placeholder(chat_id):
        if not auto_resolve:
            raise RuntimeError("chat_id is empty in %s -- run: python telegram_notify.py --resolve" % CONFIG_PATH)
        check_bot(token, bot_username)
        chat_id, _chat = resolve_chat_id(token)
        _write_chat_id(chat_id)

    return token, chat_id


def send(text, silent=False):
    """Send text as-is. Returns True on success, raises RuntimeError otherwise."""
    text = str(text)
    if not text.strip():
        raise ValueError("message is empty")

    token, chat_id = load_config()
    _call(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": "true" if silent else "false",
        },
    )
    return True


def _cmd_resolve():
    cfg = _read_config()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or str(cfg.get("bot_token", "")).strip()
    if _is_placeholder(token):
        raise RuntimeError("set bot_token in %s -- see README.md" % CONFIG_PATH)

    bot = check_bot(token, str(cfg.get("bot_username", "")).strip())
    print("bot:     @%s" % bot.get("username"))

    chat_id, chat = resolve_chat_id(token)
    _write_chat_id(chat_id)
    print("chat_id: %s  (%s)" % (chat_id, _describe(chat)))
    print("saved to %s" % CONFIG_PATH)
    return 0


def main(argv):
    args = argv[1:]
    try:
        if args and args[0] == "--resolve":
            return _cmd_resolve()
        send(" ".join(args) if args else sys.stdin.read())
    except (RuntimeError, ValueError) as exc:
        sys.stderr.write("%s\n" % exc)
        return 1
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
