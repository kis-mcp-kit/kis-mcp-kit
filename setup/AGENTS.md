# KIS Trading MCP 설치·연결 프롬프트 (AI에게 붙여넣기용)

아래 "복사 시작"부터 "복사 끝"까지를 그대로 복사해, 내 컴퓨터에서 명령을 실행할 수 있는 AI 에이전트에게 붙여 넣으세요. Claude Code, Claude Cowork(Claude Desktop의 에이전트 모드), Codex CLI(OpenAI), Cursor CLI(`cursor-agent`)가 여기에 해당합니다. 웹 채팅만 되는 도구(예: 브라우저의 ChatGPT 대화창)는 명령을 실행하지 못하므로 사람용 안내(README.md)를 따라 직접 진행하세요. 사람이 직접 따라 하는 안내는 [README.md](README.md)에 있습니다.

앱 키, 앱 시크릿, 계좌번호, HTS ID, MCP 접속 토큰은 채팅에 직접 적지 마세요. AI가 로컬 `.env` 파일 같은 안전한 방법으로 받도록 두세요.

## 사람이 먼저 해야 할 일 (붙여넣기 전에)

아래 두 가지는 AI 에이전트가 대신할 수 없습니다. 이 둘만 끝내 두면 나머지(패키지 설치, Docker 엔진, Node.js, git clone, 빌드, 서버 기동, 시세 조회)는 이 프롬프트만으로 진행됩니다(2026-09 Windows·macOS에서 Cursor·Codex로 빈 PC부터 확인).

1. **AI 에이전트 로그인.** Cursor agent, Codex CLI, Claude Code 등 쓰려는 에이전트에 사람이 직접 대화형으로 로그인해 둡니다. 로그인은 스크립트로 자동화되지 않으며, 로그인 없이 이 프롬프트를 돌리면 첫 명령에서 멈춥니다.
2. **`kis.env` 미리 만들기.** 에이전트를 실행할 작업 폴더에 사람이 만든 `kis.env`를 둡니다. 최소 항목은 KIS 모의투자 App Key·App Secret, HTS ID, 모의 계좌번호, `MCP_TYPE=sse`, `MCP_HOST=0.0.0.0`, 그리고 사람이 직접 정한 `MCP_ACCESS_TOKEN`(영문·숫자 30자 이상)입니다. 에이전트는 토큰이나 키를 스스로 만들지 않고, 값을 채팅에 출력하지도 않습니다.

그 밖에 Docker 엔진 설치와 첫 실행, 한투 계좌 개설과 키 발급, GUI 앱 재시작과 커넥터 확인도 사람 몫입니다.

---

## 복사 시작

너는 내 컴퓨터에서 한국투자증권 KIS Trading MCP를 설치하고, 실행하고, 내가 쓰는 AI 도구에 연결하는 작업을 끝까지 수행한다. 나는 자연어로만 지시하고, 명령 실행·파일 작성·검증은 네가 한다.

### 목표
1. Docker로 `kis-trade-mcp` 이미지를 빌드하고 컨테이너를 띄운다.
2. `http://127.0.0.1:3000/sse`가 HTTP 200을 돌려주는지(서버 생존) 확인한다.
3. 내가 쓰는 MCP 호스트(Claude Desktop, Cursor, Codex 중 하나)에 서버를 등록한다. ChatGPT 커넥터는 공개 HTTPS 주소만 받으므로 이 로컬 서버에는 쓰지 않는다.
4. 모의투자 기준으로 도구 호출이 되면 삼성전자(005930) 현재가를 조회해 숫자로 보여 준다.
5. 막히면 "단계 이름 + 실행한 명령 + 실제 출력 또는 오류"를 정리해 보고한다. 비밀 값은 마스킹한다.

### 성공 기준
- `http://127.0.0.1:3000/sse`가 HTTP 200과 `content-type: text/event-stream`을 돌려준다(서버 생존).
- 모의(paper) 환경에서 `005930`(삼성전자) 현재가 조회가 숫자로 돌아온다(예: `stck_prpr=259500`). 이것이 토큰까지 맞았다는 증거다.
- GUI MCP 호스트(Claude Desktop 등) 등록은 선택이다. 위 두 가지가 통과하면 설치 검증은 PASS로 본다.

### 절대 지킬 것
- 앱 키, 앱 시크릿, 계좌번호, HTS ID, `MCP_ACCESS_TOKEN`을 채팅, 스크린샷, 로그 인용에 원문으로 넣지 않는다.
- 실전 주문이나 이체를 임의로 실행하지 않는다. 학습 단계는 모의(paper) 계좌만 쓴다.
- 내가 채팅에 비밀 값을 붙여 넣으면 그 값을 쓰지 말고, 로컬 파일로 다시 받는다.

### 전제
- OS는 Windows 10/11 또는 macOS다. 명령은 OS에 맞게 바꿔라.
- 필요한 도구: 실행 중인 Docker 엔진(Docker Desktop 권장, Colima·OrbStack도 가능), Node.js와 `npx`(호스트 연결용), 인터넷.
- 한국투자증권: 모의투자 계좌, KIS Developers에서 발급한 모의용 App Key와 App Secret, HTS ID.
- 실전 키나 계좌가 없으면 자리표시자를 그대로 두고 모의만 검증한다.
- `kis.env`는 내가 작업 폴더에 미리 만들어 두었다. 토큰과 키를 네가 만들지 말고, 값을 화면에 출력하지 마라. 파일이 없거나 항목이 비어 있으면 진행을 멈추고 나에게 요청한다.
- 네가 할 수 없는 일은 나에게 요청한다: 에이전트 로그인, Docker 엔진 설치와 첫 실행, 한투 계좌 개설과 키 발급, 비밀 값 제공, GUI 앱 재시작과 커넥터 확인.

### 1단계. 저장소 받기와 이미지 빌드
```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd "open-trading-api/MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```
zip으로 받아도 되지만 한글 파일명 때문에 압축 해제 오류가 나면 `git clone`을 쓴다.

### 2단계. 환경 변수 파일 확인
작업 폴더에 내가 만들어 둔 `kis.env`가 있는지 확인하고, 아래 항목이 모두 들어 있는지 키 이름만 점검한다(값은 출력하지 않는다). 없거나 비어 있으면 나에게 요청한다. 파일은 본인만 읽을 수 있게 권한을 제한하고 Git에 올리지 않는다.
```env
KIS_PAPER_APP_KEY=...
KIS_PAPER_APP_SECRET=...
KIS_HTS_ID=...
KIS_PAPER_STOCK=...
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=<내가 직접 정한 값, 영문·숫자 30자 이상>
# 실전 값이 있으면 채우고, 없으면 자리표시자를 그대로 둔다
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
# 선물옵션 계좌(KIS_ACCT_FUTURE, KIS_PAPER_FUTURE)는 쓰지 않으므로 생략한다
```
꼭 알아 둘 것(공식 Readme 2026-07 변경, 옛 안내서에는 자주 빠져 있음):
- SSE 모드에서는 `MCP_ACCESS_TOKEN`이 필수다. 없으면 컨테이너가 바로 종료되며 로그에 `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'`가 남는다.
- 컨테이너 밖에서 접속하려면 `MCP_HOST=0.0.0.0`이어야 한다.
- 호스트 포트는 `-p 127.0.0.1:3000:3000`처럼 로컬에만 연다.
- 공식 문서는 실전 App Key/Secret을 필수로 적지만, 실측(2026-09) 결과 실전 값이 자리표시자여도 서버는 기동하고 모의 조회는 동작한다.

### 3단계. 컨테이너 실행
```bash
docker rm -f kis-trade-mcp 2>/dev/null || true
docker run -d --name kis-trade-mcp \
  -p 127.0.0.1:3000:3000 \
  --env-file /절대경로/kis.env \
  kis-trade-mcp
docker logs kis-trade-mcp
```
정상이면 로그 끝에 `Uvicorn running on http://0.0.0.0:3000` 계열 문장이 보인다. 3000번을 다른 프로그램이 쓰고 있으면 `-p 127.0.0.1:3001:3000`처럼 호스트 쪽 번호만 바꾸고 이후 URL도 3001로 맞춘다. Windows `cmd`에서는 `\` 줄 이음 대신 `^`를 쓰거나 한 줄로 적는다.

Windows에서 SSH나 무인 세션으로 작업 중이라 Docker Desktop(GUI·named pipe)에 붙지 못하면, WSL2 배포판 안에 `docker.io`(또는 Docker CE)를 설치하고 그 안에서 빌드·실행한다. WSL2 배포판은 파일 시스템은 서로 분리돼 있어도 `localhost`(127.0.0.1)는 Windows 호스트와 공유하므로, 배포판을 여러 개 띄우면 3000번이 겹친다. 그때는 배포판마다 다른 호스트 포트(3001, 3002 …)로 publish한다.

### 4단계. 기동 검증
토큰은 파일이나 변수에서만 읽고 화면에 출력하지 않는다.
```bash
curl -sS --max-time 5 -D- -o /dev/null \
  -H "Authorization: Bearer $MCP_ACCESS_TOKEN" \
  http://127.0.0.1:3000/sse
```
기대 결과: HTTP 200, `content-type: text/event-stream`. `/sse`는 끊기지 않는 스트림이라 `--max-time`이 없으면 멈춘 것처럼 보인다. 헤더만 받고 종료되면 정상이다. Windows PowerShell에서는 `$env:MCP_ACCESS_TOKEN`과 `curl.exe`를 쓴다.

주의: `/sse`는 토큰이 없거나 틀려도 200을 돌려준다(2026-09 실측). 토큰 검사는 도구 호출 시 서버 미들웨어에서 이루어지며, 틀리면 호스트 쪽에 `Unauthorized: invalid or missing MCP access token` 오류가 난다. 따라서 이 단계의 200은 서버 생존 확인이고, 토큰이 맞는지는 6단계의 모의 조회로 확인한다.

실패하면 순서대로 확인한다. (1) `docker logs`에 토큰 필수 오류가 있는지 (2) Docker 엔진(데몬)이 켜져 있는지(`docker ps`) (3) `MCP_HOST=0.0.0.0`인지 (4) 포트 매핑이 `127.0.0.1:3000:3000`인지.

### 5단계. AI 호스트 연결 (내가 쓰는 것만)
공통 원리는 `mcp-remote` + SSE URL + Authorization 헤더다.

Claude Desktop 설정 파일 위치
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
`YOUR_TOKEN_SAME_AS_ENV`는 `kis.env`의 `MCP_ACCESS_TOKEN`과 같은 값이다. 저장 후 앱을 완전히 종료하고 다시 실행한다. 커넥터 목록에 `kis-trade-mcp`가 보이면 성공이다.

Cursor, Codex는 각 제품의 MCP 설정에 같은 SSE URL과 Bearer 헤더를 넣는다. 화면은 달라도 검증 기준(도구 목록 표시, 6단계 모의 조회 성공)은 같다.

### 6단계. 기능 확인 (모의)
호스트 채팅이나 MCP 클라이언트로 도구 목록이 보이는지 확인하고, `domestic_stock`의 현재가 조회를 종목코드 `005930`(모의)으로 호출한다. 성공하면 숫자 현재가를 보고한다. 실전 키가 자리표시자면 실전 조회는 `EGW00304` 같은 키 오류가 나므로, 모의 성공만으로 설치 검증을 PASS로 본다.

### 보안
- `kis.env`는 본인만 읽을 수 있게 하고 클라우드 동기화와 화면 공유를 피한다.
- 노출이 의심되면 KIS Developers에서 키를 재발급한다.
- PC를 수리하거나 넘기기 전에 컨테이너, env 파일, 호스트 설정을 삭제한다.

### 보고 형식
```
[단계] ...
[명령] ...
[결과] PASS 또는 FAIL
[출력 요약] (비밀 값 마스킹)
[다음 할 일] ...
```

내 OS를 먼저 확인한 뒤 1단계부터 진행하라. 비밀 값이 필요하면 안전한 방법으로만 요청하라.

## 복사 끝
