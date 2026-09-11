# kis-mcp-kit

한국투자증권 KIS Trading MCP를 쓰는 개인 투자자를 위한 작은 도구 모음입니다.

| 폴더 | 내용 |
| --- | --- |
| [`setup/`](setup/) | KIS Trading MCP 설치·기동·연결. 사람용 가이드 [README.md](setup/README.md) · [README.en.md](setup/README.en.md), 에이전트용 프롬프트 [AGENTS.md](setup/AGENTS.md) · [AGENTS.en.md](setup/AGENTS.en.md) (Claude Code, Claude Cowork, Codex CLI, Cursor CLI에 붙여넣기). 2026-09 실측 반영: SSE 모드 `MCP_ACCESS_TOKEN` 필수, `MCP_HOST=0.0.0.0`, `--header Authorization: Bearer`. |
| [`telegram/`](telegram/README.md) | 파이썬 표준 라이브러리만으로 텔레그램 봇에 메시지를 보내는 한 파일 스크립트(`telegram_notify.py`). 매매 신호·체결·오류 알림용. |

키·시크릿·계좌번호·토큰은 채팅이나 저장소에 적지 말고 로컬 `.env`에만 두세요.
