from pathlib import Path
from tools.base import (
    FileDiff,
    Tool,
    ToolConfirmation,
    ToolInvocation,
    ToolKind,
    ToolResult,
)
from pydantic import BaseModel, Field, field_validator

from utils.paths import ensure_parent_directory, resolve_path


class EditParams(BaseModel):
    path: str = Field(
        ...,
        description="Path to the file to edit (relative to working directory or absolute path)",
    )
    old_string: str = Field(
        "",
        description="The exact text to find and replace. Must match exactly including all whitespace and indentation. For new files, leave this empty.",
    )
    new_string: str = Field(
        ...,
        description="The text to replace old_string with. Can be empty to delete text. MUST be different from old_string.",
    )
    replace_all: bool = Field(
        False, description="Replace all occurrences of old_string (default: false)"
    )

    @field_validator("new_string")
    def validate_strings_differ(cls, new_string, info):
        """Ensure old_string and new_string are different when old_string is provided."""
        old_string = info.data.get("old_string", "")
        if old_string and old_string == new_string:
            raise ValueError(
                "old_string and new_string must be different. "
                "They cannot be identical - this would result in no change."
            )
        return new_string


class EditTool(Tool):
    name = "edit"
    description = (
        "Edit a file by replacing text. CRITICAL: old_string and new_string MUST be different. "
        "The old_string must match exactly (including whitespace and indentation) and must be unique "
        "in the file unless replace_all is true. Include surrounding context (3-5 lines before and "
        "after) in old_string to ensure uniqueness. Use this for precise, surgical edits. "
        "For creating new files or complete rewrites, use write_file instead."
    )
    kind = ToolKind.WRITE
    schema = EditParams

    async def get_confirmation(
        self,
        invocation: ToolInvocation,
    ) -> ToolConfirmation | None:
        params = EditParams(**invocation.params)
        path = resolve_path(invocation.cwd, params.path)

        # Early validation: old_string and new_string must be different
        if params.old_string and params.old_string == params.new_string:
            return ToolConfirmation(
                tool_name=self.name,
                params=invocation.params,
                description=f"ERROR: Edit file {path} - old_string equals new_string (no-op edit)",
                diff=None,
                affected_paths=[path],
            )

        is_new_file = not path.exists()

        if is_new_file:
            diff = FileDiff(
                path=path,
                old_content="",
                new_content=params.new_string,
                is_new_file=True,
            )

            return ToolConfirmation(
                tool_name=self.name,
                params=invocation.params,
                description=f"Create new file: {path}",
                diff=diff,
                affected_paths=[path],
            )

        old_content = path.read_text(encoding="utf-8")

        if params.replace_all:
            new_content = old_content.replace(params.old_string, params.new_string)
        else:
            new_content = old_content.replace(params.old_string, params.new_string, 1)

        diff = FileDiff(
            path=path,
            old_content=old_content,
            new_content=new_content,
        )

        return ToolConfirmation(
            tool_name=self.name,
            params=invocation.params,
            description=f"Edit file: {path}",
            diff=diff,
            affected_paths=[path],
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = EditParams(**invocation.params)
        path = resolve_path(invocation.cwd, params.path)

        # Early validation: old_string and new_string must be different
        if params.old_string and params.old_string == params.new_string:
            return ToolResult.error_result(
                "EDIT ERROR: old_string equals new_string - this is a no-op edit with no effect. "
                "Either: (1) Ensure new_string is actually different from old_string, "
                "(2) Re-read the file to verify the exact text you want to replace, or "
                "(3) Verify you're making the correct change."
            )

        if not path.exists():
            if params.old_string:
                return ToolResult.error_result(
                    f"File does not exist: {path}. To create a new file, use an empty old_string."
                )

            ensure_parent_directory(path)
            path.write_text(params.new_string, encoding="utf-8")

            line_count = len(params.new_string.splitlines())

            return ToolResult.success_result(
                f"Created {path} {line_count} lines",
                diff=FileDiff(
                    path=path,
                    old_content="",
                    new_content=params.new_string,
                    is_new_file=True,
                ),
                metadata={
                    "path": str(path),
                    "is_new_file": True,
                    "lines": line_count,
                },
            )

        old_content = path.read_text(encoding="utf-8")

        if not params.old_string:
            return ToolResult.error_result(
                "old_string is empty but file exists. Provide old_string to edit, or use write_file to overwrite."
            )

        occurrence_count = old_content.count(params.old_string)

        if occurrence_count == 0:
            return self._no_match_error(params.old_string, old_content, path)

        if occurrence_count > 1 and not params.replace_all:
            return ToolResult.error_result(
                f"old_string found {occurrence_count} times in {path}. "
                f"Either: \n"
                f"1. Provide more context to make the match unique or\n"
                f"2. Set replace_all=true to replace all occurrences",
                metadata={
                    "occurence_count": occurrence_count,
                },
            )

        if params.replace_all:
            new_content = old_content.replace(params.old_string, params.new_string)
            replace_count = occurrence_count
        else:
            new_content = old_content.replace(params.old_string, params.new_string, 1)
            replace_count = 1

        # This should not occur due to early validation, but kept as safety check
        if new_content == old_content:
            return ToolResult.error_result(
                "ERROR: Replacement resulted in no change. The old_string may not have been found, "
                "or old_string and new_string are identical."
            )

        try:
            path.write_text(new_content, encoding="utf-8")
        except IOError as e:
            return ToolResult.error_result(f"failed to write file: {e}")

        old_lines = len(old_content.splitlines())
        new_lines = len(new_content.splitlines())
        line_diff = new_lines - old_lines

        diff_msg = ""

        if line_diff > 0:
            diff_msg = f" (+{line_diff} lines)"
        elif line_diff < 0:
            diff_msg = f" ({line_diff} lines)"

        return ToolResult.success_result(
            f"Edited {path}: replaced {replace_count} occurrence(s){diff_msg}",
            diff=FileDiff(path=path, old_content=old_content, new_content=new_content),
            metadata={
                "path": str(path),
                "replaced_count": replace_count,
                "line_diff": line_diff,
            },
        )

    def _no_match_error(self, old_string: str, content: str, path: Path) -> ToolResult:
        lines = content.splitlines()

        partial_matches = []
        search_terms = old_string.split()[:5]

        if search_terms:
            first_term = search_terms[0]
            for i, line in enumerate(lines, 1):
                if first_term in line:
                    partial_matches.append((i, line.strip()[:80]))
                    if len(partial_matches) >= 3:
                        break

        error_msg = f"old_string not found in {path}."

        if partial_matches:
            error_msg += "\n\nPossible similar lines:"
            for line_num, line_preview in partial_matches:
                error_msg += f"\n  Line {line_num}: {line_preview}"
            error_msg += "\n\nMake sure old_string matches exactly (including whitespace and indentation)."
        else:
            error_msg += (
                " Make sure the text matches exactly, including:\n"
                "- All whitespace and indentation\n"
                "- Line breaks\n"
                "- Any invisible characters\n"
                "Try re-reading the file using read_file tool and then editing."
            )

        return ToolResult.error_result(error_msg)
