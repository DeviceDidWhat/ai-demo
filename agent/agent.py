from __future__ import annotations
import hashlib
import json
from typing import AsyncGenerator, Awaitable, Callable
from agent.events import AgentEvent, AgentEventType
from agent.session import Session
from client.response import StreamEventType, TokenUsage, ToolCall, ToolResultMessage
from client.tool_parser import parse_tool_calls_with_errors, strip_tool_call_tags
from config.config import Config
from prompts.system import create_loop_breaker_prompt, get_prompt_based_tool_instructions
from tools.base import ToolConfirmation, ToolResult


class Agent:
    def __init__(
        self,
        config: Config,
        confirmation_callback: Callable[[ToolConfirmation], bool] | None = None,
    ):
        self.config = config
        self.session: Session | None = Session(self.config)
        self.session.approval_manager.confirmation_callback = confirmation_callback
        self._prompt_tools_injected: bool = False

    async def run(self, message: str):
        await self.session.hook_system.trigger_before_agent(message)
        yield AgentEvent.agent_start(message)
        self.session.context_manager.add_user_message(message)

        final_response: str | None = None

        async for event in self._agentic_loop():
            yield event

            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")

        await self.session.hook_system.trigger_after_agent(message, final_response)
        yield AgentEvent.agent_end(final_response)

    def _inject_prompt_based_tools(self) -> None:
        """Inject tool-calling instructions into context when native tools aren't supported."""
        if self._prompt_tools_injected:
            return
        tools = self.session.tool_registry.get_tools()
        if not tools:
            return
        instructions = get_prompt_based_tool_instructions(tools)
        self.session.context_manager.inject_system_supplement(instructions)
        self._prompt_tools_injected = True

    async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        max_turns = self.config.max_turns

        for turn_num in range(max_turns):
            self.session.increment_turn()
            response_text = ""

            # check for context overflow
            if self.session.context_manager.needs_compression():
                summary, usage = await self.session.chat_compactor.compress(
                    self.session.context_manager
                )

                if summary:
                    self.session.context_manager.replace_with_summary(summary)
                    self.session.context_manager.set_latest_usage(usage)
                    self.session.context_manager.add_usage(usage)

            # If native tools aren't supported, inject prompt-based instructions
            if not self.session.client.tools_supported:
                self._inject_prompt_based_tools()

            tool_schemas = self.session.tool_registry.get_schemas()

            tool_calls: list[ToolCall] = []
            parse_errors: list[str] = []
            usage: TokenUsage | None = None

            async for event in self.session.client.chat_completion(
                self.session.context_manager.get_messages(),
                tools=tool_schemas if tool_schemas else None,
            ):
                if event.type == StreamEventType.TEXT_DELTA:
                    if event.text_delta:
                        content = event.text_delta.content
                        response_text += content
                        yield AgentEvent.text_delta(content)
                elif event.type == StreamEventType.TOOL_CALL_COMPLETE:
                    if event.tool_call:
                        tool_calls.append(event.tool_call)
                elif event.type == StreamEventType.ERROR:
                    yield AgentEvent.agent_error(
                        event.error or "Unknown error occurred.",
                    )
                elif event.type == StreamEventType.MESSAGE_COMPLETE:
                    usage = event.usage

            # For models without native tool support, parse tool calls from text
            if not self.session.client.tools_supported and response_text:
                text_tool_calls, parse_errors = parse_tool_calls_with_errors(response_text)
                # Always strip tool_call tags from displayed response, even when parsing fails.
                response_text = strip_tool_call_tags(response_text)
                if text_tool_calls:
                    tool_calls.extend(text_tool_calls)

            self.session.context_manager.add_assistant_message(
                response_text or None,
                (
                    [
                        {
                            "id": tc.call_id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": tc.arguments if isinstance(tc.arguments, str) else str(tc.arguments),
                            },
                        }
                        for tc in tool_calls
                    ]
                    if tool_calls
                    else None
                ),
            )
            if response_text:
                yield AgentEvent.text_complete(response_text)
                self.session.loop_detector.record_action(
                    "response",
                    text=response_text,
                )

            if not tool_calls:
                # For prompt-based tools, retry once the model emits malformed tool JSON
                # instead of leaking raw tags or ending the run with no output.
                if (
                    not self.session.client.tools_supported
                    and parse_errors
                    and not response_text.strip()
                ):
                    error_lines = "\n".join(f"- {error}" for error in parse_errors[:3])
                    self.session.context_manager.add_user_message(
                        "Your previous <tool_call> block could not be parsed. "
                        "Please retry with strict JSON and valid quoting.\n\n"
                        "Requirements:\n"
                        "- Use valid JSON only\n"
                        "- Include exactly keys 'name' and 'arguments'\n"
                        "- Quote all keys and string values\n"
                        "- Example: <tool_call>{\"name\":\"write_file\",\"arguments\":{\"path\":\"styles.css\",\"content\":\"...\"}}</tool_call>\n\n"
                        f"Parser errors:\n{error_lines}"
                    )

                    if usage:
                        self.session.context_manager.set_latest_usage(usage)
                        self.session.context_manager.add_usage(usage)

                    self.session.context_manager.prune_tool_outputs()
                    continue

                if usage:
                    self.session.context_manager.set_latest_usage(usage)
                    self.session.context_manager.add_usage(usage)

                self.session.context_manager.prune_tool_outputs()
                return

            tool_call_results: list[ToolResultMessage] = []
            executed_tool_calls: set[str] = set()

            for tool_call in tool_calls:
                try:
                    if isinstance(tool_call.arguments, str):
                        parsed_args = json.loads(tool_call.arguments)
                    else:
                        parsed_args = tool_call.arguments
                except (json.JSONDecodeError, TypeError):
                    parsed_args = {}

                # Create a signature to detect duplicate tool calls within this turn
                try:
                    call_signature = f"{tool_call.name}:{json.dumps(parsed_args, sort_keys=True)}"
                    call_hash = hashlib.md5(call_signature.encode()).hexdigest()
                except (TypeError, ValueError):
                    # If arguments are not JSON serializable, use string representation
                    call_signature = f"{tool_call.name}:{str(parsed_args)}"
                    call_hash = hashlib.md5(call_signature.encode()).hexdigest()
                
                if call_hash in executed_tool_calls:
                    # Skip duplicate tool calls within the same turn
                    yield AgentEvent.tool_call_start(
                        tool_call.call_id,
                        tool_call.name,
                        parsed_args,
                    )
                    error_msg = f"Skipped duplicate tool call: {tool_call.name} with the same arguments was already executed in this turn"
                    yield AgentEvent.tool_call_complete(
                        tool_call.call_id,
                        tool_call.name,
                        ToolResult.error_result(error_msg),
                    )
                    tool_call_results.append(
                        ToolResultMessage(
                            tool_call_id=tool_call.call_id,
                            content=error_msg,
                            is_error=True,
                        )
                    )
                    continue
                
                executed_tool_calls.add(call_hash)

                yield AgentEvent.tool_call_start(
                    tool_call.call_id,
                    tool_call.name,
                    parsed_args,
                )

                self.session.loop_detector.record_action(
                    "tool_call",
                    tool_name=tool_call.name,
                    args=parsed_args,
                )

                result = await self.session.tool_registry.invoke(
                    tool_call.name,
                    parsed_args,
                    self.config.cwd,
                    self.session.hook_system,
                    self.session.approval_manager,
                )

                yield AgentEvent.tool_call_complete(
                    tool_call.call_id,
                    tool_call.name,
                    result,
                )

                tool_call_results.append(
                    ToolResultMessage(
                        tool_call_id=tool_call.call_id,
                        content=result.to_model_output(),
                        is_error=not result.success,
                    )
                )

            # For prompt-based tool calling, feed results back as a user message
            if not self.session.client.tools_supported:
                results_text = "\n\n".join(
                    f"## Tool Result: {tc.name} (id: {tc.call_id})\n{r.content}"
                    for tc, r in zip(tool_calls, tool_call_results)
                )
                self.session.context_manager.add_user_message(
                    f"Tool execution complete. Here are the results:\n\n{results_text}\n\n"
                    "Based on these results, please provide your analysis, explanation, or response. "
                    "Do NOT call the same tool again - instead, analyze the results and answer the user's question."
                )
            else:
                for tool_result in tool_call_results:
                    self.session.context_manager.add_tool_result(
                        tool_result.tool_call_id,
                        tool_result.content,
                    )

            loop_detection_error = self.session.loop_detector.check_for_loop()
            if loop_detection_error:
                loop_prompt = create_loop_breaker_prompt(loop_detection_error)
                self.session.context_manager.add_user_message(loop_prompt)

            if usage:
                self.session.context_manager.set_latest_usage(usage)
                self.session.context_manager.add_usage(usage)

            self.session.context_manager.prune_tool_outputs()
        yield AgentEvent.agent_error(f"Maximum turns ({max_turns}) reached")

    async def __aenter__(self) -> Agent:
        await self.session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        if self.session and self.session.client and self.session.mcp_manager:
            await self.session.client.close()
            await self.session.mcp_manager.shutdown()
            self.session = None
