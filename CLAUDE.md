# agent-kakao

<!-- AUTO-MANAGED: act-overview -->
## Act Overview

**Purpose:** 사용자가 업로드한 사진을 카카오 이모티콘 스타일로 변환하여 반환하는 AI 에이전트 플랫폼

**Domain:** 이미지 변환 / 이모티콘 생성 (Image Transform / Emoticon Generation)
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: casts-table -->
## Casts

| Cast | Purpose | Pattern | Location |
|------|---------|---------|----------|
| [Convert](./casts/convert/CLAUDE.md) | 사용자 업로드 사진 → 카카오 이모티콘 스타일 이미지 변환 | Sequential (Branching) | `casts/convert/` |
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: project-structure -->
## Project Structure

```
agent-kakao/
├── CLAUDE.md                  # This file
├── pyproject.toml
├── langgraph.json
├── casts/
│   ├── base_graph.py
│   ├── base_node.py
│   └── convert/               # Convert Cast
│       ├── graph.py
│       ├── pyproject.toml
│       └── modules/
│           ├── state.py
│           ├── nodes.py
│           ├── conditions.py
│           ├── tools.py
│           └── prompts.py
└── tests/
    └── cast_tests/
        └── convert_test.py
```
<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: development-commands -->
## Development Commands

```bash
# 개발 서버 실행
uv run langgraph dev

# 테스트 실행
uv run pytest tests/

# 린트 검사
uv run ruff check .

# 새 Cast 추가
uv run act cast -c "{Cast Name}"

# 의존성 추가
uv add {package-name} --directory casts/convert
```
<!-- END AUTO-MANAGED -->

<!-- MANUAL -->
## Notes

Add project-specific notes here. This section is never auto-modified.
<!-- END MANUAL -->
