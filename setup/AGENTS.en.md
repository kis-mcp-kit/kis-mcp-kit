# KIS Trading MCP setup prompt (paste into an AI agent)

Copy everything between "COPY START" and "COPY END" and paste it into an AI agent that can run commands on your machine: Claude Code, Claude Cowork (the agent mode in Claude Desktop), Codex CLI (OpenAI), or Cursor CLI (`cursor-agent`). A chat-only tool (for example the ChatGPT web chat) cannot execute commands; use the human guide (README.en.md) instead. The human-readable walkthrough is in [README.en.md](README.en.md).

Never type your App Key, App Secret, account number, HTS ID, or MCP access token into the chat. Let the agent collect them through a local `.env` file or another safe input.

## What a human must do first (before pasting)

The agent cannot do these two things for you. Once they are done, everything else (packages, Node.js, git clone, build, server start, price query) proceeds from this prompt alone (verified from a blank PC through a price query on Windows and macOS with Cursor and Codex in September 2026; orders, revisions, and cancellations were verified on a patched server with a paper account in October 2026). Installing and first-starting the Docker engine needs administrator rights, so a person does it (see below).

1. **Log in to the agent.** Sign in interactively to the agent you will use: Cursor agent, Codex CLI, Claude Code, and so on. The login cannot be scripted; running this prompt without it stops at the first command.
2. **Create `kis.env` in advance.** Put a human-made `kis.env` in the working folder where the agent runs. Minimum contents: the KIS paper-trading App Key and App Secret, the HTS ID, the paper account number, `MCP_TYPE=sse`, `MCP_HOST=0.0.0.0`, and an `MCP_ACCESS_TOKEN` you chose yourself (30+ alphanumeric characters). The agent must not invent tokens or keys, and must not print the values into the chat.

Installing and first-starting the Docker engine, opening the KIS account and issuing keys, and relaunching the GUI app to check the connector list also remain human tasks.

---

## COPY START

You are going to install, start, and connect the Korea Investment & Securities (KIS) Trading MCP server on my computer, end to end. I give instructions in plain language; you run the commands, write the files, and verify each step.

### Goals
1. Build the `kis-trade-mcp` Docker image and start the container.
2. Confirm that `http://127.0.0.1:3000/sse` returns HTTP 200 (server alive).
3. Register the server in the MCP host I use (Claude Desktop, Cursor, or Codex). ChatGPT connectors accept only a public HTTPS URL, so they are not used with this local server.
4. Once tool calls work on the paper-trading account, fetch the current price of Samsung Electronics (005930) and show me the number. If I plan to use order tools, also place a one-share limit order at 20% below the current price and cancel it immediately.
5. If you get stuck, report "step name + the exact command + the actual output or error", with secrets masked.

### Success criteria
- `http://127.0.0.1:3000/sse` returns HTTP 200 with `content-type: text/event-stream` (server alive).
- In the paper environment, a current-price query for `005930` (Samsung Electronics) returns a number (for example `stck_prpr=259500`). This proves the token is right as well.
- When testing order tools, place one share at a limit price 20% below the current price in the paper account, confirm the order number, cancel it immediately, and confirm zero open shares. A `CANO` error is FAIL.
- Registering a GUI MCP host (Claude Desktop, etc.) is optional. When the server-alive and paper-price checks pass, the installation counts as PASS.

### Hard rules
- Never put the App Key, App Secret, account number, HTS ID, or `MCP_ACCESS_TOKEN` in chat, screenshots, or quoted logs.
- Never place real orders or transfers on your own. The learning phase uses the paper (mock) account only.
- If I paste a secret into the chat, do not use it; ask me to provide it again through a local file.

### Prerequisites
- OS: Windows 10/11 or macOS. Adapt commands to the OS.
- Tools: a running Docker engine (Docker Desktop recommended; Colima or OrbStack also work), Node.js with `npx` (for host connection), internet access.
- KIS: a paper-trading account, the paper App Key and App Secret issued on KIS Developers, and the HTS ID.
- If there is no live key or account, keep the placeholders and verify with the paper account only.
- I have already placed `kis.env` in the working folder. Do not generate tokens or keys yourself and do not print the values. If the file is missing or a field is empty, stop and ask me.
- Ask me for what you cannot do yourself: logging in to the agent, installing and first-starting the Docker engine, opening the KIS account and issuing keys, providing secrets, relaunching the GUI app and checking the connector list.

### Step 1. Clone and build
```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd open-trading-api
curl -fsSL -o pr85.diff https://raw.githubusercontent.com/kis-mcp-kit/kis-mcp-kit/main/patches/pr85.diff
git apply pr85.diff
cd "MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```
The official server has a defect that makes orders, revisions, and cancellations fail with `order_cash() got an unexpected keyword argument 'CANO'`, and PR #85, which fixes it, has not been merged yet. The same PR also prevents live and paper calls made on the same day from overwriting each other's access-token files.

In Windows PowerShell, use `curl.exe` instead of `curl`. If `git apply` fails because PR #85 has since been merged into the official repository, run `git apply --reverse --check pr85.diff`; if it exits quietly, the patch is already present and can be skipped. If the image was already built without the patch, apply it, rebuild the image, and recreate the container in step 3.

A zip download also works, but if unzip fails on Korean file names, use `git clone`.

### Step 2. Check the environment file
Confirm that the `kis.env` I prepared exists in the working folder and that every key below is present (check key names only; never print values). If it is missing or a field is empty, ask me. Keep the file readable by the current user only and never commit it.
```env
KIS_PAPER_APP_KEY=...
KIS_PAPER_APP_SECRET=...
KIS_HTS_ID=...
KIS_PAPER_STOCK=...
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=<a value I chose myself, 30+ alphanumeric characters>
# fill in live values if I have them; otherwise keep the placeholders
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
# futures/options accounts (KIS_ACCT_FUTURE, KIS_PAPER_FUTURE) are not used; omit them
```
`KIS_PAPER_STOCK` is the 8-digit paper account number shown in the [나의계좌] (My Account) tab of the paper-trading site.

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

On Windows over SSH or in an unattended session, if `docker` cannot reach Docker Desktop (it depends on the GUI and a named pipe), install `docker.io` (or Docker CE) inside a WSL2 distribution and build and run there. WSL2 distributions have separate file systems but share `localhost` (127.0.0.1) with the Windows host, so running several distributions at once makes port 3000 collide; publish each on a different host port (3001, 3002, ...).

### Step 4. Verify the server
Read the token from the file or a variable; never print it.
```bash
curl -sS --max-time 5 -D- -o /dev/null \
  -H "Authorization: Bearer $MCP_ACCESS_TOKEN" \
  http://127.0.0.1:3000/sse
```
Expected: HTTP 200 with `content-type: text/event-stream`. `/sse` is an endless stream, so without `--max-time` the command looks frozen; receiving the headers and exiting is success. In Windows PowerShell use `$env:MCP_ACCESS_TOKEN` and `curl.exe`.

Note: `/sse` returns 200 even when the token is missing or wrong (measured September 2026). The token is checked by the server middleware at tool-call time; a wrong token surfaces on the host side as `Unauthorized: invalid or missing MCP access token`. So the 200 in this step only proves the server is alive; the token is verified by the paper-trading query in step 6.

If it fails, check in order: (1) the token-required error in `docker logs`, (2) the Docker engine (daemon) is running (`docker ps`), (3) `MCP_HOST=0.0.0.0`, (4) the port mapping is `127.0.0.1:3000:3000`.

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

For Codex CLI, add the following to `~/.codex/config.toml` on macOS and Linux, or `%USERPROFILE%\.codex\config.toml` on Windows.

```toml
[mcp_servers.kis-trade-mcp]
command = "npx"
args = ["-y", "mcp-remote", "http://localhost:3000/sse", "--header", "Authorization: Bearer YOUR_TOKEN_SAME_AS_ENV"]
startup_timeout_sec = 60
tool_timeout_sec = 120
default_tools_approval_mode = "approve"
```
`YOUR_TOKEN_SAME_AS_ENV` must equal `MCP_ACCESS_TOKEN` in `kis.env`. When no approval prompt is available, as with `codex exec`, `default_tools_approval_mode = "approve"` is required for Codex to use the KIS tools; without it, Codex may answer from a web search instead (measured October 2026, Codex CLI 0.162).

For Cursor, enter the same SSE URL and Bearer header in its MCP settings. The acceptance test is the same: the tool list is visible and the paper-trading query in step 6 succeeds.

### Step 6. Smoke test (paper account)
From the host chat or an MCP client, confirm the tool list is visible, then call the current-price tool under `domestic_stock` for stock code `005930` on the paper account. Report the numeric price. If the live key is a placeholder, live queries fail with a key error such as `EGW00304`; treat a successful paper query as PASS for the installation.

If order tools will be used, run "On my paper account, place a limit buy for one share of Samsung Electronics at 20% below the current price. Adjust the price to the valid tick size", confirm the order number, then run "Cancel the order I just placed" and use the order/execution history query to confirm zero open shares. Treat a `CANO` error as FAIL and recheck the patch from step 1.

### When keys or accounts change
When the three-month paper-trading participation period ends and the user applies again, the account number changes. App keys are issued separately for each account number, so use [추가신청] (Add Application) under [서비스 신청/조회] (Service Application/Status) in KIS Developers to get keys for the new number. The old row does not need to be cancelled (verified October 2026).

1. Replace `KIS_PAPER_APP_KEY` in `kis.env` with the new value.
2. Replace `KIS_PAPER_APP_SECRET` with the new value.
3. Replace `KIS_PAPER_STOCK` with the new paper account number.
4. Run `docker rm -f kis-trade-mcp`, then recreate the container with the `docker run` command in step 3.

`--env-file` is read only when the container is created, so `docker restart` does not pick up changes. Recreating the container also removes the token file created with the old key because that file is stored inside the container.

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
