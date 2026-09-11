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
cd "open-trading-api/MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```

빌드는 몇 분 걸립니다. zip으로 내려받아도 되지만, 한글 파일명 때문에 압축 해제가 실패하면 위처럼 `git clone`을 쓰세요.

## 2. 환경 변수 파일 만들기

키와 계좌 정보는 명령줄에 직접 적지 말고 파일 하나에 모읍니다. 프로젝트 폴더 밖, 클라우드 동기화가 안 되는 곳(예: 내 문서 아래 별도 폴더)에 `kis.env`라는 이름으로 만들고 아래 내용을 채웁니다.

```env
KIS_PAPER_APP_KEY=모의용 App Key
KIS_PAPER_APP_SECRET=모의용 App Secret
KIS_HTS_ID=HTS 아이디
KIS_PAPER_STOCK=모의투자 계좌번호
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

토큰 없이 호출하면 401이 나옵니다. 401은 서버가 살아 있고 토큰만 틀렸다는 뜻이라 오히려 좋은 신호입니다.

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

### Cursor, Codex, ChatGPT

각 제품의 MCP(커넥터) 설정 화면에 같은 주소 `http://localhost:3000/sse`와 같은 헤더 `Authorization: Bearer <토큰>`을 넣습니다. 화면은 달라도 확인 방법은 같습니다. 서버가 200을 돌려주고, 도구 목록이 보이면 됩니다.

## 6. 동작 확인

AI 도구 채팅창에 "모의계좌로 삼성전자 현재가 알려줘"라고 입력합니다. 숫자 현재가가 돌아오면 설치가 끝난 것입니다. 실전 키를 자리표시자로 둔 상태에서 실전 조회를 시키면 `EGW00304` 같은 키 오류가 나는데, 이는 정상이며 모의 조회 성공만으로 설치 검증은 끝입니다.

## 문제가 생겼을 때

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| 컨테이너가 켜지자마자 꺼짐. 로그에 `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'` | 접속 토큰을 넣지 않음 | `kis.env`에 `MCP_ACCESS_TOKEN`을 채우고 3단계를 다시 실행 |
| `curl`이 연결 거부 | Docker Desktop이 꺼져 있거나 컨테이너가 죽음 | Docker Desktop 실행 후 `docker ps`로 확인, 없으면 3단계 재실행 |
| 서버는 켜졌는데 밖에서 접속 불가 | `MCP_HOST`가 `127.0.0.1` | `MCP_HOST=0.0.0.0`으로 고치고 컨테이너 재생성 |
| `curl` 401 | 토큰이 다르거나 헤더 누락 | `kis.env`와 명령의 토큰이 같은지 확인 |
| 포트가 이미 사용 중 | 3000번을 다른 프로그램이 점유 | `-p 127.0.0.1:3001:3000`으로 바꾸고 주소도 3001로 |
| Claude Desktop 커넥터에 안 보임 | 설정 파일 JSON 오류, 토큰 불일치, 앱을 완전히 종료하지 않음 | 파일 문법 확인(쉼표·따옴표), 토큰 대조, 파일 → 종료 후 재실행 |
| 실전 조회에서 `EGW00304` | 실전 App Secret이 자리표시자 | 정상. 모의 조회로 검증 |

## 보안

- `kis.env`는 본인만 읽을 수 있게 하고, 클라우드 동기화 폴더와 화면 공유를 피하세요.
- 키가 노출된 것 같으면 KIS Developers에서 재발급합니다.
- 컴퓨터를 수리 맡기거나 넘기기 전에 컨테이너(`docker rm -f kis-trade-mcp`), `kis.env`, AI 도구 설정을 지웁니다.

## 참고

- 공식 저장소: https://github.com/koreainvestment/open-trading-api (MCP/Kis Trading MCP)
- 한투 공식 연결 안내: 같은 저장소의 "MCP AI 도구 연결 방법.md" (Claude Desktop, Cursor)
