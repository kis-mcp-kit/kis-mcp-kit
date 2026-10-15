# KIS Trading MCP 설치·연결 가이드 (사람용)

한국투자증권 KIS Trading MCP 서버를 내 컴퓨터에 띄우고 Claude Desktop 같은 AI 도구에 연결하는 방법입니다. 30분 정도 걸립니다. Claude Code, Claude Cowork, Codex CLI, Cursor CLI처럼 내 컴퓨터에서 명령을 실행하는 AI 에이전트에게 대신 시키고 싶다면 [AGENTS.md](AGENTS.md)의 프롬프트를 붙여 넣으세요. English version: [README.en.md](README.en.md).

## 시작하기 전에

준비물
- Windows 10/11 또는 macOS
- Docker Desktop (설치 후 실행 상태). 공식 안내는 Docker Desktop을 권장하지만 필수는 아니며, Colima·OrbStack 같은 다른 Docker 엔진이 돌아가고 있어도 됩니다.
- Node.js (AI 도구 연결에 필요한 `npx` 포함)
- 한국투자증권 모의투자 계좌, KIS Developers에서 발급한 모의용 App Key와 App Secret, HTS ID

꼭 지킬 것
- App Key, App Secret, 계좌번호, HTS ID, MCP 접속 토큰은 채팅창이나 저장소에 적지 마세요. 로컬 파일에만 둡니다.
- 처음에는 모의투자 계좌만 씁니다. 실전 키가 없어도 설치와 검증은 끝까지 할 수 있습니다.

## 사람이 직접 해야 하는 일

아래 네 가지는 AI 에이전트에게 맡길 수 없으니 미리 해 두세요.
1. Docker 엔진 설치와 첫 실행
2. 한국투자증권 계좌 개설(모의투자 계좌 포함)과 KIS Developers에서 App Key·App Secret 발급
3. AI 도구 설치와 로그인
4. 설정 후 AI 도구를 완전히 종료했다가 다시 켜고 커넥터를 눈으로 확인

## 1. 저장소 받기와 이미지 만들기

터미널(Windows는 명령 프롬프트 또는 PowerShell, macOS는 터미널)에서 차례로 실행합니다.

```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd open-trading-api
curl -fsSL -o pr85.diff https://raw.githubusercontent.com/kis-mcp-kit/kis-mcp-kit/main/patches/pr85.diff
git apply pr85.diff
cd "MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```

공식 서버에는 주문·정정·취소가 `order_cash() got an unexpected keyword argument 'CANO'`로 실패하는 결함이 있고, 이를 고치는 PR #85는 아직 합쳐지지 않았습니다. 같은 PR은 같은 날 실전·모의 호출의 접속 토큰 저장 파일이 서로 겹치는 문제도 고칩니다.

Windows PowerShell에서는 `curl` 대신 `curl.exe`를 쓰세요. 공식 저장소에 PR #85가 합쳐져 `git apply`가 실패하면 `git apply --reverse --check pr85.diff`가 조용히 끝나는지 확인하고, 그러면 패치가 이미 들어간 것이므로 건너뜁니다. 이미 패치 없이 빌드했다면 패치를 넣고 이미지를 다시 빌드한 뒤 3단계에서 컨테이너를 새로 만드세요.

빌드는 몇 분 걸립니다. zip으로 내려받아도 되지만, 한글 파일명 때문에 압축 해제가 실패하면 위처럼 `git clone`을 쓰세요.

## 2. 환경 변수 파일 만들기

키와 계좌 정보는 명령줄에 직접 적지 말고 파일 하나에 모읍니다. 클라우드 동기화 폴더나 공개 저장소가 아닌 작업 폴더(예: 내 문서 아래 별도 폴더)에 `kis.env`라는 이름으로 만들고 아래 내용을 채웁니다. AI 에이전트에게 맡길 때는 에이전트를 실행할 그 폴더에 둡니다.

```env
KIS_PAPER_APP_KEY=모의용 App Key
KIS_PAPER_APP_SECRET=모의용 App Secret
KIS_HTS_ID=HTS 아이디
KIS_PAPER_STOCK=모의투자 계좌번호 8자리(모의투자 사이트 [나의계좌] 탭)
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=직접 정한 긴 무작위 문자열(영문·숫자 30자 이상)
# 실전 값이 있으면 채우고, 없으면 아래 세 줄은 그대로 둡니다
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
```

세 가지를 기억하세요.
- `MCP_ACCESS_TOKEN`은 AI 도구가 이 서버에 들어올 때 쓰는 비밀번호입니다. 2026년 7월부터 필수가 되었습니다. 비워 두면 서버가 켜지자마자 꺼집니다.
- `MCP_HOST=0.0.0.0`이어야 컨테이너 밖(내 컴퓨터)에서 서버에 접속할 수 있습니다.
- 선물옵션 계좌 항목(`KIS_ACCT_FUTURE`, `KIS_PAPER_FUTURE`)은 쓰지 않으므로 넣지 않아도 됩니다. 실전 키가 자리표시자여도 서버는 켜지고 모의 조회는 됩니다(2026년 9월 실측).

파일을 만든 뒤에는 본인만 읽을 수 있게 권한을 제한하고, Git이나 메신저에 올리지 마세요.

## 3. 서버 켜기

```bash
docker run -d --name kis-trade-mcp \
  -p 127.0.0.1:3000:3000 \
  --env-file /kis.env의/절대경로 \
  kis-trade-mcp
docker logs kis-trade-mcp
```

Windows 명령 프롬프트에서는 줄 끝의 `\`를 `^`로 바꾸거나 한 줄로 이어 적습니다. 로그 끝에 `Uvicorn running on http://0.0.0.0:3000` 같은 문장이 보이면 정상입니다. 같은 이름의 컨테이너가 이미 있다는 오류가 나면 `docker rm -f kis-trade-mcp`로 지운 뒤 다시 실행합니다. 3000번 포트를 다른 프로그램이 쓰고 있으면 `-p 127.0.0.1:3001:3000`처럼 앞 번호만 바꾸고, 이후 주소도 3001로 맞춥니다.

`127.0.0.1:3000`은 내 컴퓨터 안에서만 접속되게 묶어 두는 설정입니다. 실전 주문 기능까지 들어 있는 서버이므로 이 제한은 풀지 마세요.

## 4. 잘 켜졌는지 확인하기

토큰 값을 넣어 서버에 한 번 접속해 봅니다. `<토큰>` 자리에 `kis.env`의 `MCP_ACCESS_TOKEN` 값을 넣습니다.

macOS 또는 Windows PowerShell:
```bash
curl -sS --max-time 5 -D- -o /dev/null -H "Authorization: Bearer <토큰>" http://127.0.0.1:3000/sse
```

`HTTP/1.1 200 OK`와 `content-type: text/event-stream`이 보이면 성공입니다. `/sse`는 끊기지 않고 계속 열려 있는 통로라서 `--max-time 5`가 없으면 명령이 멈춘 것처럼 보이는데, 5초 뒤 저절로 끝나면 정상입니다. Windows PowerShell에서는 `curl` 대신 `curl.exe`라고 적으세요.

주의할 점이 하나 있습니다. `/sse`는 토큰이 없거나 틀려도 똑같이 200을 돌려줍니다(2026년 9월 실측). 토큰은 AI 도구가 실제로 도구를 호출할 때 검사되며, 틀리면 AI 도구 쪽에 `Unauthorized: invalid or missing MCP access token` 오류가 뜹니다. 그러니 이 단계의 200은 "서버가 살아 있다"는 뜻이고, 토큰이 맞는지는 6단계의 모의 조회로 확인합니다.

## 5. AI 도구에 연결하기

원리는 하나입니다. AI 도구가 `mcp-remote`라는 작은 프로그램으로 `http://localhost:3000/sse`에 접속하되, 4단계에서 쓴 것과 같은 토큰을 헤더에 실어 보냅니다.

### Claude Desktop

설정 파일을 엽니다. Claude Desktop에서 설정 → 개발자 → 구성 편집을 누르면 파일이 열립니다. 직접 찾으려면 아래 위치입니다.
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

파일 내용을 아래처럼 만들고, `YOUR_TOKEN_SAME_AS_ENV` 자리에 `kis.env`의 `MCP_ACCESS_TOKEN` 값을 그대로 넣습니다.

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

저장한 뒤 Claude Desktop을 완전히 종료(파일 → 종료)하고 다시 실행합니다. 채팅창의 커넥터 목록에 `kis-trade-mcp`가 보이면 연결된 것입니다.

### Codex CLI

설정 파일은 macOS·Linux의 `~/.codex/config.toml`, Windows의 `%USERPROFILE%\.codex\config.toml`입니다. 아래 내용을 넣고 `YOUR_TOKEN_SAME_AS_ENV`를 `kis.env`의 `MCP_ACCESS_TOKEN`과 같은 값으로 바꿉니다.

```toml
[mcp_servers.kis-trade-mcp]
command = "npx"
args = ["-y", "mcp-remote", "http://localhost:3000/sse", "--header", "Authorization: Bearer YOUR_TOKEN_SAME_AS_ENV"]
startup_timeout_sec = 60
tool_timeout_sec = 120
default_tools_approval_mode = "approve"
```

명령 한 줄 실행(`codex exec`)처럼 허락을 묻는 창이 없을 때는 `default_tools_approval_mode = "approve"`가 있어야 한투 도구를 씁니다. 없으면 웹 검색으로 답한 일이 있습니다(2026-10, Codex CLI 0.162). 이 서버엔 주문 기능도 있으니 모의 키로 시험하세요.

### Cursor

MCP 설정 화면에 같은 주소 `http://localhost:3000/sse`와 같은 헤더 `Authorization: Bearer <토큰>`을 넣습니다. 도구 목록이 보이고 6단계의 모의 조회가 되면 됩니다. ChatGPT의 커넥터는 인터넷에서 접근되는 공개 HTTPS 주소만 받으므로, 내 컴퓨터 안(`127.0.0.1`)에만 열어 둔 이 서버에는 연결하지 않습니다.

## 6. 동작 확인

AI 도구 채팅창에 "모의계좌로 삼성전자 현재가 알려줘"라고 입력합니다. 숫자 현재가가 돌아오면 설치가 끝난 것입니다. 실전 키를 자리표시자로 둔 상태에서 실전 조회를 시키면 `EGW00304` 같은 키 오류가 나는데, 이는 정상이며 모의 조회 성공만으로 설치 검증은 끝입니다.

주문까지 쓸 거면 "모의계좌에서 삼성전자 1주를 현재가보다 20% 낮은 가격으로 지정가 매수해 줘. 가격은 호가단위에 맞게"라고 한 뒤 "방금 낸 주문 취소해 줘"라고 입력합니다. 현재가보다 한참 낮아 체결되지 않으니 돈이 들지 않고, 주문번호가 나온 뒤 취소되면 주문 기능도 정상입니다. `CANO` 오류가 나면 1단계 패치가 빠진 것입니다.

## 7. 모의투자 계좌를 다시 받았을 때

모의투자 참가 기간 3개월이 지나 다시 신청하면 계좌번호가 바뀝니다. 앱 키는 계좌번호마다 따로 발급되므로 KIS Developers [서비스 신청/조회]에서 [추가신청]을 눌러 새 계좌번호용 키를 받습니다. 예전 줄을 해지할 필요는 없습니다(2026-10 확인).

1. `kis.env`의 `KIS_PAPER_APP_KEY`를 새 값으로 바꿉니다.
2. `KIS_PAPER_APP_SECRET`을 새 값으로 바꿉니다.
3. `KIS_PAPER_STOCK`을 새 모의 계좌번호로 바꿉니다.
4. `docker rm -f kis-trade-mcp`를 실행한 뒤 3단계의 `docker run`으로 컨테이너를 다시 만듭니다.

`--env-file`은 컨테이너를 만들 때만 읽으므로 `docker restart`만 해서는 바뀌지 않습니다. 컨테이너를 새로 만들면 예전 키로 받은 토큰 저장 파일도 컨테이너와 함께 지워집니다.

## 문제가 생겼을 때

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 컨테이너가 켜지자마자 꺼짐. 로그에 `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'` | 접속 토큰을 넣지 않음 | `kis.env`에 `MCP_ACCESS_TOKEN`을 채우고 3단계를 다시 실행 |
| `curl`이 연결 거부 | Docker 엔진(Docker Desktop 등)이 꺼져 있거나 컨테이너가 죽음 | Docker 엔진 실행 후 `docker ps`로 확인, 없으면 3단계 재실행 |
| 서버는 켜졌는데 밖에서 접속 불가 | `MCP_HOST`가 `127.0.0.1` | `MCP_HOST=0.0.0.0`으로 고치고 컨테이너 재생성 |
| `/sse`는 200인데 AI 도구에서 `Unauthorized: invalid or missing MCP access token` | 토큰이 다르거나 헤더 누락(`/sse`는 토큰과 무관하게 200) | `kis.env`와 AI 도구 설정의 토큰이 같은지, 헤더가 `Authorization: Bearer <토큰>`인지 확인 |
| 포트가 이미 사용 중 | 3000번을 다른 프로그램이 점유 | `-p 127.0.0.1:3001:3000`으로 바꾸고 주소도 3001로 |
| Claude Desktop 커넥터에 안 보임 | 설정 파일 JSON 오류, 토큰 불일치, 앱을 완전히 종료하지 않음 | 파일 문법 확인(쉼표·따옴표), 토큰 대조, 파일 → 종료 후 재실행 |
| 실전 조회에서 `EGW00304` | 실전 App Secret이 자리표시자 | 정상. 모의 조회로 검증 |
| 주문·정정·취소에서 `order_cash() got an unexpected keyword argument 'CANO'` | 패치 없는 공식 서버 | 1단계의 패치를 넣고 이미지를 다시 빌드한 뒤 컨테이너 새로 만들기 |
| `기간이 만료된 token 입니다` (`EGW00123`) | 키를 바꿨는데 예전 토큰 저장 파일이 남았거나, 패치 없이 같은 날 실전·모의를 섞어 부름 | 패치를 넣고 컨테이너 새로 만들기 |
| `모의투자 처리계좌의 ID와 사용자정보가 상이` | 기간이 끝난 모의 계좌의 키 | 7절에 따라 새 계좌와 키로 바꾸기 |
| `INVALID_CHECK_ACNO` (`OPSQ2000`) | 예전 계좌로 받은 키에 새 계좌번호를 사용 | 7절에 따라 새 계좌번호용 키 받기 |
| 정정·취소 가능 주문 조회(`inquire_psbl_rvsecncl`)에서 `OPSQ0002 없는 서비스 코드` | 모의투자에서 지원하지 않는 조회 | 주문체결 조회(`inquire_daily_ccld`)로 미체결 확인(2026-10 실측) |
| SSH·무인 세션의 Windows에서 `docker` 명령이 Docker Desktop에 붙지 못함 | Docker Desktop은 GUI와 named pipe에 의존 | WSL2 배포판 안에 `docker.io`(Docker CE)를 설치하고 그 안에서 빌드·실행 |
| WSL2 배포판을 여러 개 띄웠더니 3000번 포트가 겹침 | WSL2 배포판은 파일은 분리돼도 `localhost`는 Windows 호스트와 공유 | 배포판마다 다른 호스트 포트(`-p 127.0.0.1:3001:3000` 등)로 publish |
| AI 에이전트에게 맡겼는데 첫 명령에서 멈춤 | 에이전트(Cursor·Codex·Claude Code) 로그인이 안 됐거나 `kis.env`가 작업 폴더에 없음 | 사람이 먼저 대화형 로그인을 하고 `kis.env`를 만들어 둔 뒤 다시 시작 ([AGENTS.md](AGENTS.md) 상단 참고) |

## 보안

- Claude Desktop, Cursor 등 AI 도구 설정 파일에 넣은 `MCP_ACCESS_TOKEN`은 디스크에 평문으로 남습니다. 공용 PC를 쓰거나 화면·백업을 공유할 때는 설정 파일도 함께 지우거나 토큰을 새로 정하세요.
- `kis.env`는 본인만 읽을 수 있게 하고, 클라우드 동기화 폴더와 화면 공유를 피하세요.
- 키가 노출된 것 같으면 KIS Developers에서 재발급합니다.
- 컴퓨터를 수리 맡기거나 넘기기 전에 컨테이너(`docker rm -f kis-trade-mcp`), `kis.env`, AI 도구 설정을 지웁니다.

## 참고

- 공식 저장소: https://github.com/koreainvestment/open-trading-api (MCP/Kis Trading MCP)
- 한투 공식 연결 안내: 같은 저장소의 "MCP AI 도구 연결 방법.md" (Claude Desktop, Cursor)
