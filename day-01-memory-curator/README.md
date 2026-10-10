# Conversation Memory Curator

Conversation Memory Curator turns a small transcript into reviewable memory candidates. It extracts durable facts, preferences, and commitments, removes duplicates, flags conflicting values, and preserves the source turn for every suggestion.

The tool is intentionally heuristic and local: it does not call an LLM, store data, or require an API key. Treat its output as a draft for human approval, not as an automatic memory writer.

## Structure

```text
memory_curator/
  models.py       Typed result objects
  extract.py      Candidate extraction rules
  normalize.py    Redaction, key normalization, and deduplication
  curator.py      End-to-end curation pipeline
  cli.py          JSONL input and JSON/Markdown output
tests/
  test_curator.py
examples/
  conversation.jsonl
```

## Setup

Python 3.10+ is enough; there are no third-party dependencies.

```powershell
python -m unittest discover -s tests -v
```

## Usage

Input is JSONL with one object per line and a `role` plus `content` field:

```powershell
python -m memory_curator.cli examples/conversation.jsonl --format markdown
python -m memory_curator.cli examples/conversation.jsonl --format json --min-confidence 0.7
```

Each memory includes a type, normalized key, value, confidence, evidence text, source turn, and review status. Conflicting values are reported separately so a reviewer can decide which one is current.

## Design notes

- Explicit phrases such as “I prefer” and “remember that” receive higher confidence than weak first-person statements.
- Email addresses, phone numbers, and bearer-like tokens are masked before they enter a memory candidate.
- Similar candidates are merged while their evidence turn IDs are retained.
- The parser ignores assistant messages by default because assistant claims should not become user memory without confirmation.
