# KIS Trading MCP 설치 · 연결 프롬프트 (AI에게 그대로 붙여넣기)

아래 블록 전체를 복사해서 AI(Claude / ChatGPT / Cursor 등)에게 붙여 넣고 실행을 요청하세요.
**앱 키 · 시크릿 · 계좌번호 · HTS ID · MCP 토큰은 채팅에 직접 쓰지 마세요.** AI가 안전한 입력(카드/폼/로컬 `.env`)으로 받도록 하세요.

---

## 복사 시작

너는 내 컴퓨터에서 **한국투자증권 KIS Trading MCP** 설치·기동·연결을 끝까지 수행한다.
나는 자연어로만 지시하고, 명령·파일·검증은 네가 한다.

### 목표
1. Docker로 `kis-trade-mcp` 이미지를 빌드하고 컨테이너를 띄운다.
2. `http://127.0.0.1:3000/sse` 가 Bearer 토큰과 함께 **HTTP 200** 인지 확인한다.
3. (가능하면) MCP 호스트에 서버를 등록한다. 호스트는 Claude Desktop / ChatGPT / Cursor 중 내가 쓰는 것.
4. 모의투자 기준으로 도구 호출이 되면 **삼성전자(005930) 현재가**를 조회해 숫자를 보여 준다.
5. 막히면 **절/단계 이름 + 실행한 명령 + 실제 출력/오류**(비밀 값은 마스킹)로 정리한다.

### 절대 금지
- 앱 키 / 앱 시크릿 / 계좌번호 / HTS ID / `MCP_ACCESS_TOKEN` 을 채팅·스크린샷·로그 인용에 원문으로 넣지 말 것.
- 실전 주문·이체를 임의로 실행하지 말 것. 학습 단계는 **모의(demo/paper)** 만.
- 내가 채팅에 비밀을 붙여 넣으면 **쓰지 말고** 안전한 입력으로 다시 받아라.

### 전제 확인
- OS: Windows 10/11 또는 macOS. (명령만 OS에 맞게 바꿔라.)
- 필요 도구: Docker Desktop(실행 중), Node.js/`npx`(호스트 연결 시), 인터넷.
- 한투: 모의 계좌 + KIS Developers **모의** App Key / App Secret + HTS ID.
- 실전 키/계좌가 없으면 placeholder로 두고 **모의만** 검증해도 된다.

### 저장소
```bash
git clone --depth 1 https://github.com/koreainvestment/open-trading-api.git
cd "open-trading-api/MCP/Kis Trading MCP"
docker build -t kis-trade-mcp .
```
(zip을 쓰려면 공식 main zip을 받아 같은 폴더로 들어가도 된다. 한글 파일명 unzip 오류가 나면 git clone을 써라.)

### 환경 변수 파일 (권장: `--env-file`)
프로젝트 밖, 동기화 폴더가 아닌 곳에 `kis.env`를 만들고 권한을 제한한다. Git에 올리지 마라.

필수 예 (값은 내가 안전하게 제공한다):
```env
KIS_PAPER_APP_KEY=...
KIS_PAPER_APP_SECRET=...
KIS_HTS_ID=...
KIS_PAPER_STOCK=...
KIS_PROD_TYPE=01
MCP_TYPE=sse
MCP_HOST=0.0.0.0
MCP_ACCESS_TOKEN=<강한 랜덤 토큰, 네가 생성해도 됨>
# 실전이 있으면 채우고, 없으면 your_app_key 등 placeholder 유지
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCT_STOCK=your_account
```

**중요 (공식 Readme 2026-07 이후 / 옛 원고에 자주 빠짐)**
- SSE 모드에서는 **`MCP_ACCESS_TOKEN`이 필수**다. 없으면 대략 이런 로그로 죽는다:
  `MCP_ACCESS_TOKEN must be set when MCP_TYPE is 'sse'.`
- Docker에서 호스트로 포트 포워딩하려면 컨테이너 안 바인딩이 `0.0.0.0`이어야 하므로 **`MCP_HOST=0.0.0.0`**.
- 호스트 포트는 가능하면 `-p 127.0.0.1:3000:3000` (로컬만).

### 컨테이너 실행
```bash
docker rm -f kis-trade-mcp 2>/dev/null || true
docker run -d --name kis-trade-mcp \
  -p 127.0.0.1:3000:3000 \
  --env-file /절대경로/kis.env \
  kis-trade-mcp
docker logs kis-trade-mcp
```

### 기동 검증
토큰은 변수/파일에서만 읽고 출력하지 마라.
```bash
curl -sS -D- -o /dev/null \
  -H "Authorization: Bearer $MCP_ACCESS_TOKEN" \
  http://127.0.0.1:3000/sse
```
기대: HTTP 200, `content-type` 이 `text/event-stream` 계열.

실패 시:
1) `docker logs`에 토큰 필수 오류가 있는지
2) Docker Desktop이 켜져 있는지
3) `MCP_HOST=0.0.0.0` 인지
를 먼저 본다.

### AI 호스트 연결 (쓰는 것만)
공통: `mcp-remote` + SSE URL + Authorization 헤더.

**Claude Desktop (macOS)**  
`~/Library/Application Support/Claude/claude_desktop_config.json`  
**Claude Desktop (Windows)**  
`%APPDATA%\Claude\claude_desktop_config.json`

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
설정 후 앱을 **완전 종료 후 재시작**. 커넥터에 `kis-trade-mcp`가 보이면 연결 성공.

**Cursor / ChatGPT**  
각 제품의 MCP/커넥터 UI에 동일하게 SSE URL + Bearer를 넣는다.  
호스트 UI가 달라도 MCP 서버 검증 기준(`/sse` 200 + 도구 호출)은 같다.

### 기능 스모크 (모의)
호스트 채팅 또는 MCP 클라이언트로:
- 도구 목록이 보이는지
- `domestic_stock` / 현재가 조회 / 종목코드 `005930` (모의)
성공 시 **숫자 현재가**를 보고한다.  
실전 키가 placeholder면 real 조회는 `EGW00304` 등 키 오류가 날 수 있으니, 그 경우 **모의 성공만으로 설치 검증 PASS**로 본다.

### 보안
- `.env` / `kis.env`는 본인만 읽기, 클라우드 동기화·화면공유 금지.
- 노출 의심 시 KIS Developers에서 키 재발급.
- PC 수리·양도 전 컨테이너·env·설정 삭제.

### 나에게 보고할 형식
```
[단계] ...
[명령] ...
[결과] PASS/FAIL
[출력 요약] (비밀 마스킹)
[다음 액션] ...
```

자, 내 OS를 확인한 뒤 1단계부터 진행하고, 비밀이 필요하면 안전한 입력으로만 요청해라.

## 복사 끝
