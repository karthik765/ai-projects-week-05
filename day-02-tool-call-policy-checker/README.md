# Tool Call Policy Checker

Tool-using AI agents can propose actions that are outside an application's safety boundary. This small, dependency-free utility checks a batch of model-generated tool calls against a local policy before execution.

It produces an explainable `allow`, `review`, or `deny` decision. Findings identify the call, rule, severity, and evidence that triggered the rule. The checker is intentionally deterministic: it does not call an API and does not pretend to replace authorization or human approval.

## Features

- allowlist and explicit blocklist checks for tool names;
- blocked argument-key detection for secrets or sensitive fields;
- confirmation requirements for high-impact tools;
- batch call limits and a capped 0–100 risk score;
- human-readable and JSON CLI output;
- standard-library-only implementation with automated tests.

## Run it

From this directory, run:

```text
python -m unittest discover -s tests -v
python -m tool_policy.cli examples/sample_batch.json
python -m tool_policy.cli examples/sample_batch.json --json
```

The sample exits with status 1 because sending email requires review. Integrate the checker before dispatching a tool call, and treat `review` as a handoff to the application's confirmation flow. Policies should be versioned and reviewed with the same care as other authorization rules.

## Input shape

The JSON file contains a `policy` object and a `calls` array. A call has a string `name` and an object `arguments`. See `examples/sample_batch.json` for a complete example.
