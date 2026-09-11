# KIS Trading MCP setup prompt (paste into an AI agent)

Copy everything between "COPY START" and "COPY END" and paste it into an AI agent that can run commands on your machine: Claude Code, Claude Cowork (the agent mode in Claude Desktop), Codex CLI (OpenAI), or Cursor CLI (`cursor-agent`). A chat-only tool (for example the ChatGPT web chat) cannot execute commands; use the human guide (README.en.md) instead. The human-readable walkthrough is in [README.en.md](README.en.md).

Never type your App Key, App Secret, account number, HTS ID, or MCP access token into the chat. Let the agent collect them through a local `.env` file or another safe input.

---

## COPY START

You are going to install, start, and connect the Korea Investment & Securities (KIS) Trading MCP server on my computer, end to end. I give instructions in plain language; you run the commands, write the files, and verify each step.

### Goals
1. Build the `kis-trade-mcp` Docker image and start the container.
2. Confirm that `http://127.0.0.1:3000/sse` returns HTTP 200 when called with a Bearer token.
3. Register the server in the MCP host I use (Claude Desktop, Cursor, Codex, or ChatGPT connectors).
4. Once tool calls work on the paper-trading account, fetch the current price of Samsung Electronics (005930) and show me the number.
5. If you get stuck, report "step name + the exact command + the actual output or error", with secrets masked.

### Hard rules
- Never put the App Key, App Secret, account number, HTS ID, or `MCP_ACCESS_TOKEN` in chat, screenshots, or quoted logs.
- Never place real orders or transfers on your own. The learning phase uses the paper (mock) account only.
- If I paste a secret into the chat, do not use it; ask me to provide it again through a local file.

### Prerequisites
- OS: Windows 10/11 or macOS. Adapt commands to the OS.
- Tools: a running Docker engine (Docker Desktop recommended; Colima or OrbStack also work), Node.js with `npx` (for host connection), internet access.
- KIS: a paper-trading account, the paper App Key and App Secret issued on KIS Developers, and the HTS ID.
- If there is no live key or account, keep the placeholders and verify with the paper account only.
- Ask me for what you cannot do yourself: installing and first-starting the Docker engine, opening the KIS account and issuing keys, providing secrets, relaunching the GUI app and checking the connector list.

### Step 1. Clone and build
```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd "open-trading-api/MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```
A zip download also works, but if unzip fails on Korean file names, use `git clone`.

### Step 2. Create the environment file
Create `kis.env` outside the project folder and outside any cloud-synced folder, restrict it to the current user, and never commit it. I will provide the values through a safe channel.
```env
KIS_PAPER_APP_KEY=...
KIS_PAPER_APP_SECRET=...
KIS_HTS_ID=...
KIS_PAPER_STOCK=...
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=<a strong random token you generate, 30+ alphanumeric characters>
# fill in live values if I have them; otherwise keep the placeholders
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
# futures/options accounts (KIS_ACCT_FUTURE, KIS_PAPER_FUTURE) are not used; omit them
```
Important (changed in the official README in July 2026; older guides miss it):
- In SSE mode `MCP_ACCESS_TOKEN` is required. Without it the container exits immediately and the log shows `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'`.
- To reach the server from outside the container, `MCP_HOST` must be `0.0.0.0`.
- Publish the port to localhost only: `-p 127.0.0.1:3000:3000`.
- The official README lists the live App Key/Secret as required, but as measured in September 2026 the server starts with placeholder live values and paper queries work.

### Step 3. Run the container
```bash
docker rm -f kis-trade-mcp 2>/dev/null || true
docker run -d --name kis-trade-mcp \
  -p 127.0.0.1:3000:3000 \
  --env-file /absolute/path/kis.env \
  kis-trade-mcp
docker logs kis-trade-mcp
```
A healthy start ends with a line like `Uvicorn running on http://0.0.0.0:3000`. If port 3000 is taken, change only the host side, e.g. `-p 127.0.0.1:3001:3000`, and use 3001 in every URL below. In Windows `cmd`, use `^` instead of `\` for line continuation or write the command on one line.

### Step 4. Verify the server
Read the token from the file or a variable; never print it.
```bash
curl -sS --max-time 5 -D- -o /dev/null \
  -H "Authorization: Bearer $MCP_ACCESS_TOKEN" \
  http://127.0.0.1:3000/sse
```
Expected: HTTP 200 with `content-type: text/event-stream`. `/sse` is an endless stream, so without `--max-time` the command looks frozen; receiving the headers and exiting is success. In Windows PowerShell use `$env:MCP_ACCESS_TOKEN` and `curl.exe`.

If it fails, check in order: (1) the token-required error in `docker logs`, (2) Docker Desktop is running, (3) `MCP_HOST=0.0.0.0`, (4) a call without the header returns 401, which means the server is fine and only the token is wrong.

### Step 5. Connect the AI host (only the one I use)
Common pattern: `mcp-remote` + the SSE URL + an Authorization header.

Claude Desktop config file
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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
`YOUR_TOKEN_SAME_AS_ENV` must equal `MCP_ACCESS_TOKEN` in `kis.env`. Quit the app completely and start it again. When `kis-trade-mcp` appears in the connector list, the connection works.

For Cursor, Codex, or ChatGPT connectors, enter the same SSE URL and Bearer header in the product's MCP settings. The screens differ, but the acceptance test is the same: `/sse` returns 200 and tool calls succeed.

### Step 6. Smoke test (paper account)
From the host chat or an MCP client, confirm the tool list is visible, then call the current-price tool under `domestic_stock` for stock code `005930` on the paper account. Report the numeric price. If the live key is a placeholder, live queries fail with a key error such as `EGW00304`; treat a successful paper query as PASS for the installation.

### Security
- Make `kis.env` readable by the current user only; keep it out of cloud sync and screen sharing.
- If a key may have leaked, reissue it on KIS Developers.
- Before repairing or handing over the PC, delete the container, the env file, and the host configuration.

### Report format
```
[Step] ...
[Command] ...
[Result] PASS or FAIL
[Output summary] (secrets masked)
[Next action] ...
```

Detect my OS first, then start from Step 1. Ask for secrets only through a safe channel.

## COPY END
