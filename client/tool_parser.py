"""
Parse tool calls from model text output for models without native tool calling.

Models that don't support the OpenAI tools API are instructed to emit tool calls
in their text response using the format:

    <tool_call>
    {"name": "tool_name", "arguments": {"param": "value"}}
    </tool_call>

This module extracts those blocks and converts them into ToolCall objects.
"""

import json
import re
import uuid
from client.response import ToolCall


_TOOL_CALL_PATTERN = re.compile(
    r"<tool_call>\s*(.*?)\s*</tool_call>",
    re.DOTALL,
)

_UNQUOTED_KEY_PATTERN = re.compile(r'([\{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:')
_TRAILING_COMMA_PATTERN = re.compile(r",\s*([}\]])")


def _repair_common_json_issues(raw: str) -> str:
    """Repair common JSON mistakes from model output before parsing."""
    repaired = _UNQUOTED_KEY_PATTERN.sub(r'\1"\2":', raw)
    repaired = _TRAILING_COMMA_PATTERN.sub(r"\1", repaired)
    return repaired


def _load_tool_call_json(raw: str) -> tuple[dict | None, str | None]:
    """Parse tool JSON with a single repair pass for common formatting issues."""
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as first_error:
        repaired = _repair_common_json_issues(raw)
        if repaired == raw:
            return None, str(first_error)

        try:
            return json.loads(repaired), None
        except json.JSONDecodeError as second_error:
            return None, str(second_error)


def parse_tool_calls_with_errors(text: str) -> tuple[list[ToolCall], list[str]]:
    """Extract tool calls and collect parse errors for malformed blocks."""
    tool_calls: list[ToolCall] = []
    parse_errors: list[str] = []

    for index, match in enumerate(_TOOL_CALL_PATTERN.finditer(text), start=1):
        raw = match.group(1).strip()
        data, parse_error = _load_tool_call_json(raw)
        if data is None:
            snippet = raw.replace("\n", " ")[:120]
            parse_errors.append(
                f"Block {index}: invalid JSON ({parse_error}). Snippet: {snippet}"
            )
            continue

        name = data.get("name")
        if not name:
            parse_errors.append(f"Block {index}: missing required key 'name'.")
            continue

        arguments = data.get("arguments", {})
        if isinstance(arguments, str):
            try:
                args_dict = json.loads(arguments)
                arguments_json = json.dumps(args_dict)
            except json.JSONDecodeError:
                arguments_json = json.dumps({"raw_arguments": arguments})
        else:
            arguments_json = json.dumps(arguments)

        tool_calls.append(
            ToolCall(
                call_id=f"tc_{uuid.uuid4().hex[:8]}",
                name=name,
                arguments=arguments_json,
            )
        )

    return tool_calls, parse_errors


def parse_tool_calls_from_text(text: str) -> list[ToolCall]:
    """Extract tool call blocks from model text output."""
    tool_calls, _ = parse_tool_calls_with_errors(text)
    return tool_calls


def strip_tool_call_tags(text: str) -> str:
    """Remove <tool_call>...</tool_call> blocks from text, returning only prose."""
    return _TOOL_CALL_PATTERN.sub("", text).strip()
