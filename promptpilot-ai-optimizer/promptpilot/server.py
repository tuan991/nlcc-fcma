"""MCP stdio server exposing local PromptPilot tools to compatible clients."""
from mcp.server.fastmcp import FastMCP
from .core import (build_prompt, clean_text, compact_text, compare_text, create_handoff,
                   estimate_tokens, inspect_project, make_coding_prompt, prioritize_context,
                   redact_secrets, compact_json_text, extract_relevant_snippets)

mcp = FastMCP("PromptPilot Extreme Token Optimizer")

@mcp.tool()
def clean_text_tool(text: str, remove_repeated_blank_lines: bool = True) -> str:
    """Normalize whitespace without summarizing or removing substantive content."""
    return clean_text(text, remove_repeated_blank_lines)

@mcp.tool()
def compact_text_tool(text: str, deduplicate_lines: bool = True) -> dict:
    """Conservatively compact text and report measured size change."""
    compacted = compact_text(text, deduplicate_lines)
    return {"text": compacted, "measurement": compare_text(text, compacted)}

@mcp.tool()
def estimate_tokens_tool(text: str) -> dict:
    """Estimate a broad token range; not an exact Claude tokenizer count."""
    return estimate_tokens(text)

@mcp.tool()
def compare_size_tool(before: str, after: str) -> dict:
    """Measure character and word changes."""
    return compare_text(before, after)

@mcp.tool()
def build_prompt_tool(task: str, requirements: str = "", source_material: str = "", output_limit: str = "", compact: bool = True) -> str:
    """Build a compact copy-ready prompt."""
    return build_prompt(task, requirements, source_material, output_limit, compact)

@mcp.tool()
def create_handoff_tool(summary: str, decisions: str = "", open_questions: str = "", next_steps: str = "", compact: bool = True) -> str:
    """Create a concise handoff note for a new chat."""
    return create_handoff(summary, decisions, open_questions, next_steps, compact)

@mcp.tool()
def prioritize_context_tool(items: list[dict], max_characters: int) -> dict:
    """Select whole context items by priority; inspect excluded items."""
    return prioritize_context(items, max_characters)

@mcp.tool()
def redact_secrets_tool(text: str) -> dict:
    """Best-effort mask common API keys and credentials before sharing text."""
    return redact_secrets(text)

@mcp.tool()
def make_coding_prompt_tool(task: str, constraints: str = "", diff_first: bool = True, output_budget: str = "") -> str:
    """Generate a coding prompt that favors minimal diffs and targeted tests."""
    return make_coding_prompt(task, constraints, diff_first, output_budget)

@mcp.tool()
def inspect_project_tool(root: str, query: str = "", max_files: int = 20, max_characters: int = 18000,
                         include_extensions: list[str] | None = None, include_file_contents: bool = True) -> dict:
    """Create a bounded, relevance-ranked local project map and sanitized file context. Review before sending."""
    return inspect_project(root, query, max_files, max_characters, include_extensions, include_file_contents)


def main() -> None:
    mcp.run(transport="stdio")


@mcp.tool()
def compact_json_tool(text: str) -> dict:
    """Minify valid JSON while preserving its parsed data; invalid JSON is returned unchanged."""
    return compact_json_text(text)

@mcp.tool()
def extract_relevant_snippets_tool(root: str, query: str, max_characters: int = 9000,
                                  context_lines: int = 3, max_snippets: int = 20,
                                  include_extensions: list[str] | None = None) -> dict:
    """Return ranked exact source snippets under a character budget instead of whole project files."""
    return extract_relevant_snippets(root, query, max_characters, context_lines, max_snippets, include_extensions)
