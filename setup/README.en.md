# KIS Trading MCP setup guide (for people)

How to run the Korea Investment & Securities (KIS) Trading MCP server on your own computer and connect it to an AI tool such as Claude Desktop. It takes about 30 minutes. If you would rather have an AI agent that can run commands on your machine (Claude Code, Claude Cowork, Codex CLI, Cursor CLI) do it for you, paste the prompt in [AGENTS.en.md](AGENTS.en.md). 한국어 안내: [README.md](README.md).

## Before you start

You need
- Windows 10/11 or macOS
- Docker Desktop, installed and running. The official guide recommends Docker Desktop, but it is not strictly required; any running Docker engine (Colima, OrbStack, etc.) works.
- Node.js (it provides `npx`, used to connect the AI tool)
- A KIS paper-trading account, the paper App Key and App Secret issued on KIS Developers, and your HTS ID

Two rules
- Never type the App Key, App Secret, account number, HTS ID, or MCP access token into a chat window or a repository. Keep them in a local file only.
- Start with the paper account. You can finish the whole setup and verification without a live key.

## What you must do yourself

These four things cannot be delegated to an AI agent, so do them first.
1. Install the Docker engine and start it once
2. Open a KIS account (including the paper-trading account) and issue the App Key and App Secret on KIS Developers
3. Install the AI tool and sign in
4. After configuration, quit and relaunch the AI tool and check the connector list yourself

## 1. Clone the repository and build the image

Run these in a terminal (Command Prompt or PowerShell on Windows, Terminal on macOS).

```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd "open-trading-api/MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```

The build takes a few minutes. A zip download also works, but if unzip fails on Korean file names, use `git clone` as above.

## 2. Create the environment file

Instead of typing keys on the command line, put them in one file. Create `kis.env` outside the project folder and outside any cloud-synced folder, and fill it in like this.

```env
KIS_PAPER_APP_KEY=paper App Key
KIS_PAPER_APP_SECRET=paper App Secret
KIS_HTS_ID=your HTS ID
KIS_PAPER_STOCK=paper account number
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=a long random string you choose (30+ letters and digits)
# fill in live values if you have them; otherwise leave these three lines as they are
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
```

Three things to remember.
- `MCP_ACCESS_TOKEN` is the password the AI tool uses to enter this server. It became mandatory in July 2026. If it is empty, the server exits right after starting.
- `MCP_HOST=0.0.0.0` is what lets your computer (outside the container) reach the server.
- The futures/options account fields (`KIS_ACCT_FUTURE`, `KIS_PAPER_FUTURE`) are not used, so you can leave them out. The server starts and paper queries work even when the live key lines are placeholders (verified September 2026).

After creating the file, restrict it to your own user account and never upload it to Git or a messenger.

## 3. Start the server

```bash
docker run -d --name kis-trade-mcp \
  -p 127.0.0.1:3000:3000 \
  --env-file /absolute/path/to/kis.env \
  kis-trade-mcp
docker logs kis-trade-mcp
```

In Windows Command Prompt, replace the trailing `\` with `^` or write the command on one line. A line like `Uvicorn running on http://0.0.0.0:3000` at the end of the log means the server is up. If Docker says a container with that name already exists, remove it with `docker rm -f kis-trade-mcp` and run again. If port 3000 is already in use, change only the first number, e.g. `-p 127.0.0.1:3001:3000`, and use 3001 in every address below.

`127.0.0.1:3000` keeps the server reachable from your own computer only. The server includes live-order tools, so do not loosen this.

## 4. Check that it is running

Call the server once with your token. Replace `<TOKEN>` with the `MCP_ACCESS_TOKEN` value from `kis.env`.

macOS or Windows PowerShell:
```bash
curl -sS --max-time 5 -D- -o /dev/null -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:3000/sse
```

`HTTP/1.1 200 OK` with `content-type: text/event-stream` means success. `/sse` is an endless stream, so without `--max-time 5` the command looks frozen; it ending by itself after five seconds is normal. In Windows PowerShell type `curl.exe` instead of `curl`.

One caveat: `/sse` answers 200 even when the token is missing or wrong (measured September 2026). The token is checked when the AI tool actually calls a tool; a wrong token shows up on the AI tool side as `Unauthorized: invalid or missing MCP access token`. So a 200 here means "the server is alive"; whether the token is right is confirmed by the paper-trading query in step 6.

## 5. Connect an AI tool

The idea is the same everywhere: the AI tool runs a small helper called `mcp-remote` that opens `http://localhost:3000/sse` and sends the same token from step 4 in a header.

### Claude Desktop

Open the config file. In Claude Desktop go to Settings → Developer → Edit Config, or open it directly:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Make the file look like this, replacing `YOUR_TOKEN_SAME_AS_ENV` with the `MCP_ACCESS_TOKEN` value from `kis.env`.

```json
{
  "mcpServers": {
    "kis-trade-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:3000/sse",
        "--header",
        "Authorization: Bearer YOUR_TOKEN_SAME_AS_ENV"
      ]
    }
  }
}
```

Save, quit Claude Desktop completely (File → Quit), and start it again. When `kis-trade-mcp` appears in the connector list of the chat window, you are connected.

### Cursor, Codex

Enter the same address `http://localhost:3000/sse` and the same header `Authorization: Bearer <TOKEN>` in the product's MCP settings. The screens differ, but the check is the same: the tool list is visible and the paper-trading query in step 6 works. ChatGPT connectors accept only a public HTTPS URL reachable from the internet, so they are not used with this server, which is bound to `127.0.0.1` on your own machine.

## 6. Try it

In the AI tool's chat, type "Show me the current price of Samsung Electronics on my paper account". A numeric price means the setup is complete. If you left the live key as a placeholder and ask for a live query, you get a key error such as `EGW00304`; that is expected, and a successful paper query is all the verification you need.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Container exits immediately; log says `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'` | Access token missing | Fill `MCP_ACCESS_TOKEN` in `kis.env` and repeat step 3 |
| `curl` says connection refused | Docker engine (Docker Desktop, etc.) not running or container stopped | Start the Docker engine, check `docker ps`, repeat step 3 if needed |
| Server is up but unreachable from outside | `MCP_HOST` is `127.0.0.1` | Set `MCP_HOST=0.0.0.0` and recreate the container |
| `/sse` returns 200 but the AI tool shows `Unauthorized: invalid or missing MCP access token` | Token differs or header missing (`/sse` returns 200 regardless of the token) | Compare the token in `kis.env` and in the AI tool settings; the header must be `Authorization: Bearer <TOKEN>` |
| Port already in use | Another program uses 3000 | Use `-p 127.0.0.1:3001:3000` and 3001 in the addresses |
| Not shown in Claude Desktop connectors | JSON syntax error, token mismatch, app not fully quit | Check commas and quotes, compare tokens, File → Quit and relaunch |
| `EGW00304` on a live query | Live App Secret is a placeholder | Expected; verify with the paper account |
| On Windows over SSH or unattended, `docker` cannot reach Docker Desktop | Docker Desktop depends on the GUI and a named pipe | Install `docker.io` (Docker CE) inside a WSL2 distribution and build/run there |
| Several WSL2 distributions collide on port 3000 | WSL2 distributions have separate file systems but share `localhost` with the Windows host | Publish each on a different host port (`-p 127.0.0.1:3001:3000`, etc.) |
| You delegated to an AI agent and it stops at the first command | The agent (Cursor, Codex, Claude Code) is not logged in, or `kis.env` is not in the working folder | Log in interactively and create `kis.env` first, then restart (see the top of [AGENTS.en.md](AGENTS.en.md)) |

## Security

- The `MCP_ACCESS_TOKEN` you put in the AI tool's config file (Claude Desktop, Cursor, etc.) stays on disk in plain text. On a shared PC, or when sharing screens or backups, delete that config file too or choose a new token.
- Keep `kis.env` readable by your user only, out of cloud-synced folders, and off screen shares.
- If a key may have leaked, reissue it on KIS Developers.
- Before repairing or handing over the computer, delete the container (`docker rm -f kis-trade-mcp`), `kis.env`, and the AI tool configuration.

## References

- Official repository: https://github.com/koreainvestment/open-trading-api (MCP/Kis Trading MCP)
- KIS connection guide in the same repository: "MCP AI 도구 연결 방법.md" (Claude Desktop, Cursor)
