# kis-mcp-kit

한국투자증권 KIS Trading MCP를 쓰는 개인 투자자를 위한 작은 도구 모음입니다.

| 폴더 | 내용 |
| --- | --- |
| [`setup/`](setup/) | KIS Trading MCP 설치·기동·연결. 사람용 가이드 [README.md](setup/README.md) · [README.en.md](setup/README.en.md), 에이전트용 프롬프트 [AGENTS.md](setup/AGENTS.md) · [AGENTS.en.md](setup/AGENTS.en.md) (Claude Code, Claude Cowork, Codex CLI, Cursor CLI에 붙여넣기). 2026-09 실측 반영: SSE 모드 `MCP_ACCESS_TOKEN` 필수, `MCP_HOST=0.0.0.0`, `--header Authorization: Bearer`. |
| [`telegram/`](telegram/README.md) | 파이썬 표준 라이브러리만으로 텔레그램 봇에 메시지를 보내는 한 파일 스크립트(`telegram_notify.py`). 매매 신호·체결·오류 알림용. |

키·시크릿·계좌번호·토큰은 채팅이나 저장소에 적지 말고 로컬 `.env`에만 두세요.

## 면책 · 범위

- 이 저장소는 한국투자증권·OpenAI·Anthropic 등과 무관한 비공식 자료입니다.
- 투자·주문으로 인한 손실에 대해 작성자/기여자는 책임지지 않습니다. 모의투자로 먼저 검증하세요.
- KIS Trading MCP는 실전 주문 도구를 포함할 수 있습니다. 포트는 `127.0.0.1`에만 묶고, 토큰·키는 저장소/채팅에 올리지 마세요.
- 공식 API·MCP 동작은 업스트림(https://github.com/koreainvestment/open-trading-api) 기준이며, 이 가이드는 2026-09 실측을 반영한 보조 문서입니다.

## 라이선스

MIT ([LICENSE](LICENSE))
