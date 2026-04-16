from pathlib import Path
from typing import Any
import sys
from rich.console import Console
from rich.theme import Theme
from rich.rule import Rule
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.console import Group
from rich.syntax import Syntax
from config.config import Config
from tools.base import ToolConfirmation
from utils.paths import display_path_rel_to_cwd
import re

from utils.text import truncate_text

# ── Color Palette ──────────────────────────────────────────────────────
# A refined dark-terminal palette with teal/cyan accents

AGENT_THEME = Theme(
    {
        # General
        "info": "bright_cyan",
        "warning": "yellow",
        "error": "bright_red bold",
        "success": "bright_green",
        "dim": "dim",
        "muted": "grey58",
        "border": "grey35",
        "highlight": "bold bright_cyan",
        "accent": "bright_magenta",
        # Brand
        "brand": "bold bright_cyan",
        "brand.sub": "cyan",
        # Roles
        "user": "bold bright_white",
        "user.prompt": "bold bright_cyan",
        "assistant": "bright_white",
        "assistant.label": "bold bright_cyan",
        # Tools
        "tool": "bold bright_magenta",
        "tool.read": "bright_cyan",
        "tool.write": "bright_yellow",
        "tool.shell": "bright_magenta",
        "tool.network": "bright_blue",
        "tool.memory": "bright_green",
        "tool.mcp": "bright_cyan",
        # Code / blocks
        "code": "white",
        # Status
        "status.running": "bold yellow",
        "status.done": "bold bright_green",
        "status.failed": "bold bright_red",
    }
)

_console: Console | None = None

AITAS_LOGO_LARGE = (
    "     \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\n"
    "    \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551\u255a\u2550\u2550\u2588\u2588\u2554\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\n"
    "    \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\n"
    "    \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u255a\u2550\u2550\u2550\u2550\u2588\u2588\u2551\n"
    "    \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\n"
    "    \u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d   \u255a\u2550\u255d   \u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d"
)

# Minimum terminal width needed to render the large logo inside a panel
# Logo is ~48 chars wide + 2 border + 2*2 padding = 56
_LOGO_MIN_WIDTH = 58

AITAS_TAGLINE = "AI Terminal Automation System"

# ── Tool Icons (ASCII-safe) ────────────────────────────────────────────
TOOL_ICONS = {
    "read_file": "[R] ",
    "write_file": "[W] ",
    "edit": "[E] ",
    "shell": "[>] ",
    "glob": "[*] ",
    "grep": "[?] ",
    "list_dir": "[D] ",
    "web_search": "[S] ",
    "web_fetch": "[F] ",
    "memory": "[M] ",
    "todos": "[T] ",
}

STATUS_ICONS = {
    "running": "~ ",
    "success": "+ ",
    "failure": "x ",
}


def get_console() -> Console:
    global _console
    if _console is None:
        # Ensure stdout supports Unicode on Windows (cp1252 -> utf-8)
        if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        _console = Console(theme=AGENT_THEME, highlight=False)

    return _console


class TUI:
    def __init__(
        self,
        config: Config,
        console: Console | None = None,
    ) -> None:
        self.console = console or get_console()
        self._assistant_stream_open = False
        self._tool_args_by_call_id: dict[str, dict[str, Any]] = {}
        self.config = config
        self.cwd = self.config.cwd
        self._max_block_tokens = 2500

    # ── Assistant streaming ────────────────────────────────────────────

    def begin_assistant(self) -> None:
        self.console.print()
        label = Text.assemble(
            (" AITAS ", "bold white on bright_cyan"),
            ("", ""),
        )
        self.console.print(label)
        self.console.print()
        self._assistant_stream_open = True

    def end_assistant(self) -> None:
        if self._assistant_stream_open:
            self.console.print()
            self.console.print(Rule(style="grey30"))
        self._assistant_stream_open = False

    def stream_assistant_delta(self, content: str) -> None:
        self.console.print(content, end="", markup=False)

    # ── Tool argument helpers ──────────────────────────────────────────

    def _ordered_args(self, tool_name: str, args: dict[str, Any]) -> list[tuple]:
        _PREFERRED_ORDER = {
            "read_file": ["path", "offset", "limit"],
            "write_file": ["path", "create_directories", "content"],
            "edit": ["path", "replace_all", "old_string", "new_string"],
            "shell": ["command", "timeout", "cwd"],
            "list_dir": ["path", "include_hidden"],
            "grep": ["path", "case_insensitive", "pattern"],
            "glob": ["path", "pattern"],
            "todos": ["id", "action", "content"],
            "memory": ["action", "key", "value"],
        }

        preferred = _PREFERRED_ORDER.get(tool_name, [])
        ordered: list[tuple[str, Any]] = []
        seen = set()

        for key in preferred:
            if key in args:
                ordered.append((key, args[key]))
                seen.add(key)

        remaining_keys = set(args.keys() - seen)
        ordered.extend((key, args[key]) for key in remaining_keys)

        return ordered

    def _render_args_table(self, tool_name: str, args: dict[str, Any]) -> Table:
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bright_cyan", justify="right", no_wrap=True)
        table.add_column(style="code", overflow="fold")

        for key, value in self._ordered_args(tool_name, args):
            if isinstance(value, str):
                if key in {"content", "old_string", "new_string"}:
                    line_count = len(value.splitlines()) or 0
                    byte_count = len(value.encode("utf-8", errors="replace"))
                    value = f"<{line_count} lines | {byte_count} bytes>"

            # Convert non-string values to strings for rendering
            if not isinstance(value, str):
                value = str(value)

            table.add_row(f"{key}:", value)

        return table

    # ── Tool call panels ───────────────────────────────────────────────

    def tool_call_start(
        self,
        call_id: str,
        name: str,
        tool_kind: str | None,
        arguments: dict[str, Any],
    ) -> None:
        self._tool_args_by_call_id[call_id] = arguments
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"

        icon = TOOL_ICONS.get(name, " ")

        title = Text.assemble(
            (f"{icon}{name}", "tool"),
            ("  ", ""),
            (f"#{call_id[:8]}", "muted"),
        )

        display_args = dict(arguments)
        for key in ("path", "cwd"):
            val = display_args.get(key)
            if isinstance(val, str) and self.cwd:
                display_args[key] = str(display_path_rel_to_cwd(val, self.cwd))

        status_text = Text.assemble(
            (STATUS_ICONS["running"], "status.running"),
            ("running", "status.running"),
        )

        panel = Panel(
            (
                self._render_args_table(name, display_args)
                if display_args
                else Text(
                    "(no args)",
                    style="muted",
                )
            ),
            title=title,
            title_align="left",
            subtitle=status_text,
            subtitle_align="right",
            border_style=border_style,
            box=box.HEAVY,
            padding=(0, 2),
        )
        self.console.print()
        self.console.print(panel)

    # ── File content helpers ───────────────────────────────────────────

    def _extract_read_file_code(self, text: str) -> tuple[int, str] | None:
        body = text
        header_match = re.match(r"^Showing lines (\d+)-(\d+) of (\d+)\n\n", text)

        if header_match:
            body = text[header_match.end() :]

        code_lines: list[str] = []
        start_line: int | None = None

        for line in body.splitlines():
            m = re.match(r"^\s*(\d+)\|(.*)$", line)
            if not m:
                return None
            line_no = int(m.group(1))
            if start_line is None:
                start_line = line_no
            code_lines.append(m.group(2))

        if start_line is None:
            return None

        return start_line, "\n".join(code_lines)

    def _guess_language(self, path: str | None) -> str:
        if not path:
            return "text"
        suffix = Path(path).suffix.lower()
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".json": "json",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".kt": "kotlin",
            ".swift": "swift",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".css": "css",
            ".html": "html",
            ".xml": "xml",
            ".sql": "sql",
        }.get(suffix, "text")

    # ── Welcome screen ─────────────────────────────────────────────────

    def print_welcome(self, title: str, lines: list[str]) -> None:
        term_width = self.console.size.width

        # Build header: large logo if terminal is wide enough, else compact text
        header_parts = []
        if term_width >= _LOGO_MIN_WIDTH:
            logo_text = Text()
            logo_lines = AITAS_LOGO_LARGE.split("\n")
            colors = [
                "bright_cyan",
                "bright_cyan",
                "cyan",
                "cyan",
                "bright_blue",
                "bright_blue",
            ]
            for i, line in enumerate(logo_lines):
                color = colors[i % len(colors)]
                logo_text.append(line + "\n", style=color)
            header_parts.append(logo_text)
            header_parts.append(Text(f"    {AITAS_TAGLINE}\n", style="bold white"))
        else:
            header_parts.append(Text("AITAS", style="bold bright_cyan"))
            header_parts.append(Text(f" {AITAS_TAGLINE}\n", style="bold white"))

        # Responsive separator using Rule
        header_parts.append(Rule(style="grey35"))

        # Config info table (grid tables are inherently responsive)
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="bright_cyan", justify="right", no_wrap=True)
        info_table.add_column(style="white", overflow="fold")

        labels = {
            "provider": None,
            "model": None,
            "cwd": None,
            "commands": None,
        }
        for line in lines:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key and val:
                labels[key] = val

        for key, val in labels.items():
            if val:
                info_table.add_row(f"  {key}", val)

        header_parts.append(info_table)

        panel = Panel(
            Group(*header_parts),
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()

    # ── Tool call complete ─────────────────────────────────────────────

    def tool_call_complete(
        self,
        call_id: str,
        name: str,
        tool_kind: str | None,
        success: bool,
        output: str,
        error: str | None,
        metadata: dict[str, Any] | None,
        diff: str | None,
        truncated: bool,
        exit_code: int | None,
    ) -> None:
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"
        status_key = "success" if success else "failure"
        status_label = "done" if success else "failed"
        status_style = "status.done" if success else "status.failed"

        icon = TOOL_ICONS.get(name, " ")

        title = Text.assemble(
            (f"{STATUS_ICONS[status_key]}", status_style),
            (f"{icon}{name}", "tool"),
            ("  ", ""),
            (f"#{call_id[:8]}", "muted"),
        )

        args = self._tool_args_by_call_id.get(call_id, {})

        primary_path = None
        blocks = []
        if isinstance(metadata, dict) and isinstance(metadata.get("path"), str):
            primary_path = metadata.get("path")

        if name == "read_file" and success:
            if primary_path:
                start_line, code = self._extract_read_file_code(output)

                shown_start = metadata.get("shown_start")
                shown_end = metadata.get("shown_end")
                total_lines = metadata.get("total_lines")
                pl = self._guess_language(primary_path)

                header_parts = [display_path_rel_to_cwd(primary_path, self.cwd)]
                header_parts.append("  |  ")

                if shown_start and shown_end and total_lines:
                    header_parts.append(
                        f"lines {shown_start}-{shown_end} of {total_lines}"
                    )

                header = "".join(header_parts)
                blocks.append(Text(header, style="muted"))
                blocks.append(
                    Syntax(
                        code,
                        pl,
                        theme="monokai",
                        line_numbers=True,
                        start_line=start_line,
                        word_wrap=True,
                    )
                )
            else:
                output_display = truncate_text(
                    output,
                    "",
                    self._max_block_tokens,
                )
                blocks.append(
                    Syntax(
                        output_display,
                        "text",
                        theme="monokai",
                        word_wrap=True,
                    )
                )
        elif name in {"write_file", "edit"} and success and diff:
            output_line = output.strip() if output.strip() else "Completed"
            blocks.append(Text(output_line, style="muted"))
            diff_text = diff
            diff_display = truncate_text(
                diff_text,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    diff_display,
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "shell" and success:
            command = args.get("command")
            if isinstance(command, str) and command.strip():
                blocks.append(Text(f"$ {command.strip()}", style="bright_yellow"))

            if exit_code is not None:
                ec_style = "success" if exit_code == 0 else "error"
                blocks.append(Text(f"exit code: {exit_code}", style=ec_style))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "list_dir" and success:
            entries = metadata.get("entries")
            path = metadata.get("path")
            summary = []
            if isinstance(path, str):
                summary.append(path)

            if isinstance(entries, int):
                summary.append(f"{entries} entries")

            if summary:
                blocks.append(Text("  |  ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "grep" and success:
            matches = metadata.get("matches")
            files_searched = metadata.get("files_searched")
            summary = []
            if isinstance(matches, int):
                summary.append(f"{matches} matches")
            if isinstance(files_searched, int):
                summary.append(f"searched {files_searched} files")

            if summary:
                blocks.append(Text("  |  ".join(summary), style="muted"))

            output_display = truncate_text(
                output, self.config.model_name, self._max_block_tokens
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "glob" and success:
            matches = metadata.get("matches")
            if isinstance(matches, int):
                blocks.append(Text(f"{matches} matches", style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "web_search" and success:
            results = metadata.get("results")
            query = args.get("query")
            summary = []
            if isinstance(query, str):
                summary.append(query)
            if isinstance(results, int):
                summary.append(f"{results} results")

            if summary:
                blocks.append(Text("  |  ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "web_fetch" and success:
            status_code = metadata.get("status_code")
            content_length = metadata.get("content_length")
            url = args.get("url")
            summary = []
            if isinstance(status_code, int):
                summary.append(str(status_code))
            if isinstance(content_length, int):
                summary.append(f"{content_length} bytes")
            if isinstance(url, str):
                summary.append(url)

            if summary:
                blocks.append(Text("  |  ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "todos" and success:
            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "memory" and success:
            action = args.get("action")
            key = args.get("key")
            found = metadata.get("found")
            summary = []
            if isinstance(action, str) and action:
                summary.append(action)
            if isinstance(key, str) and key:
                summary.append(key)
            if isinstance(found, bool):
                summary.append("found" if found else "missing")

            if summary:
                blocks.append(Text("  |  ".join(summary), style="muted"))
            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        else:
            if error and not success:
                blocks.append(Text(f"ERROR: {error}", style="error"))

            output_display = truncate_text(
                output, self.config.model_name, self._max_block_tokens
            )
            if output_display.strip():
                blocks.append(
                    Syntax(
                        output_display,
                        "text",
                        theme="monokai",
                        word_wrap=True,
                    )
                )
            else:
                blocks.append(Text("(no output)", style="muted"))

        if truncated:
            blocks.append(Text("note: output was truncated", style="warning"))

        status_text = Text.assemble(
            (status_label, status_style),
        )

        panel = Panel(
            Group(
                *blocks,
            ),
            title=title,
            title_align="left",
            subtitle=status_text,
            subtitle_align="right",
            border_style=border_style,
            box=box.HEAVY,
            padding=(0, 2),
        )
        self.console.print()
        self.console.print(panel)

    # ── Confirmation dialog ────────────────────────────────────────────

    def handle_confirmation(self, confirmation: ToolConfirmation) -> bool:
        output = [
            Text(confirmation.tool_name, style="tool"),
            Text(confirmation.description, style="code"),
        ]

        if confirmation.command:
            output.append(Text(f"$ {confirmation.command}", style="bright_yellow"))

        if confirmation.diff:
            diff_text = confirmation.diff.to_diff()
            output.append(
                Syntax(
                    diff_text,
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                )
            )

        self.console.print()
        self.console.print(
            Panel(
                Group(*output),
                title=Text(" Approval Required ", style="bold yellow"),
                title_align="left",
                border_style="yellow",
                box=box.DOUBLE,
                padding=(1, 2),
            )
        )

        response = Prompt.ask(
            "\n[bold bright_cyan]Approve?[/bold bright_cyan]",
            choices=["y", "n", "yes", "no"],
            default="n",
        )

        return response.lower() in {"y", "yes"}

    # ── Help screen ────────────────────────────────────────────────────

    def show_help(self) -> None:
        help_items = [
            ("Session", [
                ("/help", "Show this help"),
                ("/exit, /quit", "Exit AITAS"),
                ("/clear", "Clear conversation"),
                ("/stats", "Session statistics"),
            ]),
            ("Configuration", [
                ("/config", "Show current config"),
                ("/model <name>", "Change model"),
                ("/approval <mode>", "Change approval mode"),
                ("/tools", "List available tools"),
                ("/mcp", "MCP server status"),
            ]),
            ("Persistence", [
                ("/save", "Save current session"),
                ("/sessions", "List saved sessions"),
                ("/resume <id>", "Resume a session"),
                ("/checkpoint [name]", "Create checkpoint"),
                ("/checkpoints", "List checkpoints"),
                ("/restore <id>", "Restore checkpoint"),
            ]),
        ]

        sections = []
        for section_name, commands in help_items:
            table = Table(
                show_header=True,
                header_style="bold bright_cyan",
                box=box.SIMPLE_HEAVY,
                border_style="grey35",
                padding=(0, 1),
                expand=True,
            )
            table.add_column("Command", style="bright_yellow", no_wrap=True, ratio=2)
            table.add_column("Description", style="white", ratio=3)

            for cmd, desc in commands:
                table.add_row(cmd, desc)

            sections.append(Text(f"\n  {section_name}", style="bold bright_cyan"))
            sections.append(table)

        tips = Text("\n  Tips\n", style="bold bright_cyan")
        tips_content = Text()
        tips_content.append("  - Type your message to chat with AITAS\n", style="white")
        tips_content.append("  - Press Ctrl+C to cancel the current task\n", style="white")
        tips_content.append("  - AITAS can read, write, and execute code\n", style="white")

        sections.append(tips)
        sections.append(tips_content)

        panel = Panel(
            Group(*sections),
            title=Text(" AITAS Help ", style="bold bright_cyan"),
            title_align="left",
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(0, 2),
        )
        self.console.print()
        self.console.print(panel)
