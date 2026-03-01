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
        # Convert arguments to JSON string for storage in ToolCall
        if isinstance(arguments, str):
            # If already a string, try to parse and re-serialize as valid JSON
            try:
                args_dict = json.loads(arguments)
                arguments_json = json.dumps(args_dict)
            except json.JSONDecodeError:
                # If invalid JSON string, store it as raw arguments in a dict
                arguments_json = json.dumps({"raw_arguments": arguments})
        else:
            # If it's a dict or other type, serialize to JSON
            arguments_json = json.dumps(arguments)

        tool_calls.append(
            ToolCall(
                call_id=f"tc_{uuid.uuid4().hex[:8]}",
                name=name,
                arguments=arguments_json,
            )
        )

    return tool_calls


def strip_tool_call_tags(text: str) -> str:
    """Remove <tool_call>...</tool_call> blocks from text, returning only prose."""
    return _TOOL_CALL_PATTERN.sub("", text).strip()
