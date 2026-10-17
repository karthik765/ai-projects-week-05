# Context Window Planner

Long conversations need a predictable way to fit inside an LLM context window. This dependency-free utility estimates message tokens, keeps required system and recent context, and fills the remaining budget with the most useful older messages.

## Features

- Deterministic token estimation with a documented approximation
- Required-message preservation for system instructions and pinned context
- Recency and priority scoring for optional messages
- Explicit dropped-message reasons and budget warnings
- Human-readable or JSON CLI output
- No API keys, network calls, or model-specific SDKs

## Input format

Provide a JSON array of messages. Each message needs `role` and `content`; `priority`, `pinned`, and `metadata` are optional.

```json
[
  {"role": "system", "content": "You are a helpful assistant.", "pinned": true},
  {"role": "user", "content": "What did we decide last week?", "priority": 2}
]
```

## Run

From this directory:

```text
python -m context_planner examples/conversation.json --budget 90
python -m context_planner examples/conversation.json --budget 90 --json
python -m unittest discover -s tests -v
```

The report includes estimated usage, selected message indexes, dropped messages, and warnings when pinned content alone exceeds the budget. The estimate is intentionally conservative and is not a replacement for a tokenizer supplied by a target model provider.
