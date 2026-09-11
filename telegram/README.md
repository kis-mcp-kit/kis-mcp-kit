# telegram_notify

Send a text message to your own Telegram chat from a Python script.
One file, no dependencies — just the standard library.

Useful for pushing trade signals, fills, or errors to your phone.

## Setup

You fill in two things about the bot you create. The script works out the
rest on its own.

### 1. Create a bot

In Telegram, message [@BotFather](https://t.me/BotFather) and send `/newbot`.
Give it a display name and a username ending in `bot`.

BotFather replies with a token like `123456789:AAHfiqksKZ8...` — copy the whole string.

### 2. Fill in the config

Edit `telegram_config.txt`. Leave `chat_id` empty:

```json
{
  "bot_token": "123456789:AAHfiqksKZ8...",
  "bot_username": "my_assistant_bot",
  "chat_id": ""
}
```

### 3. Say hello to your bot

Open your new bot in Telegram and send it `/start`.

> This step is not optional. A bot cannot start a conversation — Telegram
> only lets it write to someone who messaged it first. That first message is
> also how the script learns where to send.

### 4. Test

```bash
python telegram_notify.py "hello"
```

Prints `sent`, the message appears in your chat, and `chat_id` is filled in
and cached in the config so later sends skip the lookup.

To do the lookup without sending anything:

```bash
python telegram_notify.py --resolve
```

```
bot:     @my_assistant_bot
chat_id: 123456789  (Your Name (@yourhandle))
saved to .../telegram_config.txt
```

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

| Key | You set it? | Meaning |
|---|---|---|
| `bot_token` | yes | From BotFather |
| `bot_username` | optional | Checked against the token, to catch a pasted wrong token |
| `chat_id` | no | Filled in automatically; who the bot sends to |

Environment variables override the file, which is handy for CI or for
keeping the token out of a shared folder: `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_CHAT_ID`.

If more than one person has messaged the bot, the script cannot guess which
one you mean and will list the candidates — put the right number in `chat_id`.

## Troubleshooting

| Message | Cause |
|---|---|
| `set bot_token in ...` | Config still has the placeholder values |
| `config file not found` | `telegram_config.txt` is missing or renamed |
| `nobody has messaged this bot yet` | Step 3 was skipped — send `/start` |
| `bot_token belongs to @x, but bot_username says @y` | Token and bot name disagree |
| `telegram api error 401` | Token is wrong or was revoked |
| `telegram api error 404` | Token is malformed |
| `telegram connection failed` | No network, or a proxy is blocking api.telegram.org |

## Security

`telegram_config.txt` holds a live credential. Anyone with the token can
post as your bot, so do not commit it to a public repository. If it leaks,
send `/revoke` to BotFather and paste the new token into the config.
