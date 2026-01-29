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


def parse_tool_calls_from_text(text: str) -> list[ToolCall]:
    """Extract tool call blocks from model text output."""
    tool_calls: list[ToolCall] = []

    for match in _TOOL_CALL_PATTERN.finditer(text):
        raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        name = data.get("name")
        if not name:
            continue

        arguments = data.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw_arguments": arguments}

        tool_calls.append(
            ToolCall(
                call_id=f"tc_{uuid.uuid4().hex[:8]}",
                name=name,
                arguments=arguments,
            )
        )

    return tool_calls


def strip_tool_call_tags(text: str) -> str:
    """Remove <tool_call>...</tool_call> blocks from text, returning only prose."""
    return _TOOL_CALL_PATTERN.sub("", text).strip()
