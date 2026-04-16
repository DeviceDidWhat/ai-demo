#!/usr/bin/env python3
"""Regression tests for prompt-based tool call parsing."""

from client.tool_parser import parse_tool_calls_with_errors, strip_tool_call_tags


def test_repairs_unquoted_keys() -> None:
    text = """<tool_call>
{"name":"write_file","arguments":{"content":"x",path:"styles.css"}}
</tool_call>"""

    tool_calls, parse_errors = parse_tool_calls_with_errors(text)

    assert len(tool_calls) == 1, "Expected one repaired tool call"
    assert tool_calls[0].name == "write_file"
    assert '"path": "styles.css"' in tool_calls[0].arguments
    assert not parse_errors, f"Did not expect parse errors, got: {parse_errors}"


def test_reports_invalid_json_and_strips_tags() -> None:
    text = """<tool_call>
{"name":"write_file","arguments":{"content":"x","path":}}
</tool_call>"""

    tool_calls, parse_errors = parse_tool_calls_with_errors(text)

    assert len(tool_calls) == 0, "Expected no parsed calls for invalid JSON"
    assert parse_errors, "Expected parse errors for invalid JSON"
    assert strip_tool_call_tags(text) == "", "Tool tags should always be removed from display text"


if __name__ == "__main__":
    test_repairs_unquoted_keys()
    test_reports_invalid_json_and_strips_tags()
    print("All tool parser tests passed")