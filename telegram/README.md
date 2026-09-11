# telegram_notify

Send a text message to your own Telegram chat from a Python script.
One file, no dependencies — just the standard library.

Useful for pushing trade signals, fills, or errors to your phone.

## Setup

### 1. Create a bot

In Telegram, message [@BotFather](https://t.me/BotFather) and send `/newbot`.
Give it a display name and a username ending in `bot`.

BotFather replies with a token like `123456789:AAHfiqksKZ8...` — copy the whole string.

### 2. Get your chat id

Open your new bot and send it `/start`. Then open this URL in a browser,
replacing `<TOKEN>` with your token:

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

Find `"chat":{"id":123456789` in the response. That number is your chat id.

> A bot cannot message you first — Telegram only allows it after you
> have messaged the bot. If `getUpdates` comes back empty, send `/start` again.

### 3. Fill in the config

Edit `telegram_config.txt`:

```json
{
  "bot_token": "123456789:AAHfiqksKZ8...",
  "chat_id": "123456789"
}
```

### 4. Test

```bash
python telegram_notify.py "hello"
```

Prints `sent` and the message appears in your chat.

## Usage

From the command line:

```bash
python telegram_notify.py "BUY 005930 x73 @259500"
```

From a pipe:

```bash
echo "daily report done" | python telegram_notify.py
```

From Python:

```python
from telegram_notify import send

send("BUY 005930 x73 @259500 (order 0000012345)")
send("market closed, no orders placed", silent=True)
```

`send()` returns `True`, or raises `RuntimeError` with the reason.
Text is sent as-is — no Markdown or HTML parsing, so `<`, `&`, and `*`
are safe to include.

## Config

Values are read from `telegram_config.txt` next to the script.
Environment variables override the file, which is handy for CI or
for keeping the token out of a shared folder:

| Variable | Overrides |
|---|---|
| `TELEGRAM_BOT_TOKEN` | `bot_token` |
| `TELEGRAM_CHAT_ID` | `chat_id` |

## Troubleshooting

| Message | Cause |
|---|---|
| `set bot_token and chat_id in ...` | Config still has the placeholder values |
| `config file not found` | `telegram_config.txt` is missing or renamed |
| `telegram api error 401` | Token is wrong or was revoked |
| `telegram api error 400` | Chat id is wrong, or you never sent `/start` |
| `telegram connection failed` | No network, or a proxy is blocking api.telegram.org |

## Security

`telegram_config.txt` holds a live credential. Anyone with the token can
post as your bot, so do not commit it to a public repository. If it leaks,
send `/revoke` to BotFather and paste the new token into the config.
