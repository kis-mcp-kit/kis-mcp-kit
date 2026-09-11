# kis-mcp-kit

한국투자증권 KIS Trading MCP를 쓰는 개인 투자자를 위한 작은 도구 모음입니다.

| 폴더 | 내용 |
| --- | --- |
| [`setup/`](setup/README.md) | KIS Trading MCP 설치·기동·연결 프롬프트. 블록 전체를 AI(Claude / ChatGPT / Cursor)에게 붙여 넣으면 Docker 빌드부터 `/sse` 검증, 호스트 연결까지 진행합니다. 2026-09 실측 반영(SSE 모드 `MCP_ACCESS_TOKEN` 필수, `MCP_HOST=0.0.0.0`, `--header Authorization: Bearer`). |
| [`telegram/`](telegram/README.md) | 파이썬 표준 라이브러리만으로 텔레그램 봇에 메시지를 보내는 한 파일 스크립트(`telegram_notify.py`). 매매 신호·체결·오류 알림용. |

키·시크릿·계좌번호·토큰은 채팅이나 저장소에 적지 말고 로컬 `.env`에만 두세요.
