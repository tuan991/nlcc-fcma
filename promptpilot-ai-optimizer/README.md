# PromptPilot AI Optimizer — V4 Super Saver

A local-first toolkit to reduce avoidable prompt overhead, clean repeated text, prioritize context under a budget, and create concise handoffs between AI sessions. Optional MCP integration lets Claude Desktop and other MCP-compatible clients call the tools.

**Design goal: maximum practical savings without silently changing meaning.** PromptPilot does not claim to know Claude's exact tokenization and does not secretly modify a model's active context. All measurements are local character/word counts; token estimates are rough ranges only.

## What it does

- **Compact prompt builder:** concise labels and minimal generic instructions; supports verbose mode for comparison.
- **Conservative text compaction:** normalize whitespace and remove exact repeated non-empty lines. It does not paraphrase, summarize, remove stop words, or rewrite code/URLs.
- **Context budget selector:** select whole context items by explicit priority under a character budget; report every excluded item so omissions are visible. Review before sending.
- **Compact handoff:** carry forward project state, decisions, open questions, and next steps without a long template.
- **Measured comparison:** compare before/after characters and words, including percentage reduction.
- **Token planning:** rough mixed-language range, not an exact Claude tokenizer.
- **Local-first privacy:** no API key, telemetry, cloud service, or automatic chat/file access.

## Important limitations

1. **No universal “extreme token saving” switch exists.** Removing meaningful details can make the model wrong or force expensive follow-up turns. This tool favors safe, measurable formatting savings and makes context omissions explicit.
2. Character reduction is not identical to token reduction. Vietnamese, English, code, tables, and JSON tokenize differently by model.
3. The context selector uses character budgets, not token budgets. Its priority choices are only as good as the priorities you provide.
4. The MCP server only processes text explicitly passed to its tools; it cannot inspect or clear Claude's private conversation history.

## Requirements

- Python 3.10+
- Claude Desktop or another MCP-compatible client (optional)

## Install and test (Windows PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s . -p 'tests_*.py' -v
.\.venv\Scripts\python.exe benchmark.py
```

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s . -p 'tests_*.py' -v
.venv/bin/python benchmark.py
```

The MCP server uses stdio and may show no normal terminal output when launched directly. That is expected; the client sends requests through the stdio connection.

## Claude Desktop configuration

Find the absolute path to this repository and its virtual-environment Python executable. Common config locations:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the following server entry, replacing both example paths. Preserve any existing `mcpServers` entries:

```json
{
  "mcpServers": {
    "promptpilot": {
      "command": "C:\\path\\to\\promptpilot-ai-optimizer\\.venv\\Scripts\\python.exe",
      "args": ["-m", "promptpilot"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\promptpilot-ai-optimizer"
      }
    }
  }
}
```

Restart Claude Desktop. Exact configuration details can vary by client/version; check the client's current MCP documentation if the server does not appear.

## MCP tools

- `clean_text_tool(text, remove_repeated_blank_lines=true)`
- `compact_text_tool(text, deduplicate_lines=true)` — returns compacted text and measured size change.
- `estimate_tokens_tool(text)` — rough range, not exact tokenization.
- `compare_size_tool(before, after)`
- `build_prompt_tool(task, requirements, source_material, output_limit, compact=true)`
- `create_handoff_tool(summary, decisions, open_questions, next_steps, compact=true)`
- `prioritize_context_tool(items, max_characters)` — returns selected and excluded items.

## How to get the largest safe savings

1. Send only the relevant section of a document, not an entire file when only one section matters.
2. Remove exact duplicate lines and formatting noise locally before asking an AI to summarize.
3. Put task, constraints, source, and output limit into one clear request.
4. Use a compact handoff at task boundaries; retain decisions, hard constraints, current state, and next actions.
5. Give context items explicit priorities and inspect all excluded items before use.
6. Specify a useful output limit and format. Do not make the limit so tight that the model omits required facts.
7. Keep a source of truth for long projects. A short handoff should point to key facts, not pretend to preserve every detail.
8. Measure each transformation. Reject a “saving” that removes important meaning or causes extra correction turns.

## Reproducible effectiveness test

Run `python benchmark.py`. It compares verbose and compact prompt/handoff templates and removes repeated lines from a fixed sample. It prints actual character/word changes and percentage character reduction for each case. Results are deterministic for the included examples and may not represent a user's real workload. `python -m unittest discover -s . -p 'tests_*.py' -v` validates compactness, idempotence, source preservation, budget handling, and error cases.

## Privacy and safety

PromptPilot processes only arguments explicitly passed to its tools. It does not automatically read chat history or local files. Avoid sending secrets, passwords, API keys, or personal data. Review excluded context items and generated prompts before sharing.

## Contributing

Issues and pull requests are welcome. Include a reproducible input, expected behavior, actual measurements, and tests. Please avoid claims of exact token savings unless verified with the relevant model tokenizer.

## License

MIT — see [LICENSE](LICENSE).

## V3 Extreme features

V3 adds local-first helpers designed for large coding tasks:

- **`inspect_project_tool`**: makes a relevance-ranked project inventory and selects a bounded amount of text from likely relevant files. It skips common generated/dependency folders, oversized files and known credential filenames. It attempts best-effort secret masking before returning contents. Review the selected context and redactions before sending it to any AI.
- **`redact_secrets_tool`**: masks common API-key formats and private-key blocks. This is only a safety net, not a guarantee; do not use it as the sole secret-scanning control.
- **`make_coding_prompt_tool`**: creates a short coding instruction that favors focused diffs, relevant-file inspection and targeted tests rather than rewriting whole files.
- Existing compact prompt, handoff, context prioritization, cleanup and rough-size tools remain available.

### Integration with Claude Desktop

1. Install Python 3.10 or newer.
2. Extract this repository to a stable local folder.
3. Open a terminal in that folder and run `python -m pip install -e .`.
4. Add a server entry to Claude Desktop's MCP configuration, replacing the path with the actual absolute path on your machine:

```json
{
  "mcpServers": {
    "promptpilot": {
      "command": "python",
      "args": ["-m", "promptpilot"],
      "cwd": "C:\\path\\to\\promptpilot-ai-optimizer"
    }
  }
}
```

If your Claude Desktop build/configuration does not support `cwd`, use the absolute path to the environment's Python and launch the installed `promptpilot-mcp` command, or follow the current Claude Desktop MCP configuration instructions. Restart Claude Desktop after changing the config. Keep the server local; it reads project files only when you invoke the project-inspection tool.

### What this can and cannot optimize

PromptPilot reduces avoidable text and helps select relevant context; it does not change Claude's model, context window, plan limits, or billing rules. The token estimate is approximate, not Claude's exact tokenizer. Prompt caching is controlled by the Claude client/API and model-specific rules; this MCP tool does not force caching or guarantee cache hits. For API applications, evaluate Claude's official prompt-caching support separately. The biggest practical savings usually come from sending only relevant files, reusing stable instructions appropriately, asking for minimal diffs, and limiting unnecessary output—not from aggressively deleting meaningful words.

### Validation

Run tests with `python -m unittest discover -s . -p 'tests_*.py' -v` and syntax checks with `python -m compileall -q promptpilot`. End-to-end MCP startup requires installing the declared `mcp` dependency; tests of the core do not validate Claude Desktop connectivity.


## V4 Super Saver

V4 adds two focused savings tools without requiring an external API:

- **`extract_relevant_snippets_tool`** searches local source files and returns ranked, exact line windows around query matches under a character budget. This can avoid sending entire large files. It is heuristic, not full code dependency analysis; inspect tests/callers and excluded context before making changes.
- **`compact_json_tool`** minifies valid JSON by parsing and re-serializing it. The parsed data is preserved, but original indentation/formatting is not. Invalid JSON is returned unchanged.

The safest large savings usually come from reducing *which context is sent*, not deleting words from meaningful requirements or source code. JSON minification is appropriate for payloads, not for human-readable documentation. Snippet search is best used to locate likely relevant code, followed by a targeted review of related callers, tests, configuration and types.

### V4 tools

- `compact_json_tool(text)` — safe parsed-data-preserving JSON minification.
- `extract_relevant_snippets_tool(root, query, max_characters=9000, context_lines=3, max_snippets=20, include_extensions=None)` — ranked exact source windows with an explicit size budget.
