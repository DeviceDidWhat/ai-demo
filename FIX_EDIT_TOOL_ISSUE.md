# Edit Tool Issue - Root Cause Analysis & Fixes

## Problem: "No change made - old_string equals new_string" Error

**Symptom:** When the model uses the `edit` tool, it occasionally generates tool calls where `old_string` and `new_string` are identical, resulting in a no-op edit and the error: `ERROR: No change made - old_string equals new_string`

**Root Causes:**
1. The LLM accidentally generates a tool call where it copies the same text to both parameters
2. Whitespace handling confusion - the model may perceive whitespace differently than it actually exists in the file
3. The model being confused about what exact text needs to be changed
4. Poor guidance in the tool description about the requirement that the strings must differ

## Fixes Implemented

### 1. **Schema-Level Validation** (`tools/builtin/edit_file.py`)
Added a Pydantic field validator to the `EditParams` class that ensures `old_string` and `new_string` are different when `old_string` is provided:

```python
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
```

This validation will raise an error during parameter parsing if the strings are identical.

### 2. **Early Validation in Execute Method**
Added a check at the beginning of the `execute()` method to catch this issue before attempting any file operations:

```python
# Early validation: old_string and new_string must be different
if params.old_string and params.old_string == params.new_string:
    return ToolResult.error_result(
        "EDIT ERROR: old_string equals new_string - this is a no-op edit with no effect. "
        "Either: (1) Ensure new_string is actually different from old_string, "
        "(2) Re-read the file to verify the exact text you want to replace, or "
        "(3) Verify you're making the correct change."
    )
```

This provides immediate feedback to the model with actionable guidance.

### 3. **Early Validation in Get Confirmation Method**
Added the same check to `get_confirmation()` so the user sees the error in the preview before execution:

```python
# Early validation: old_string and new_string must be different
if params.old_string and params.old_string == params.new_string:
    return ToolConfirmation(
        tool_name=self.name,
        params=invocation.params,
        description=f"ERROR: Edit file {path} - old_string equals new_string (no-op edit)",
        diff=None,
        affected_paths=[path],
    )
```

### 4. **Improved Tool Description**
Updated the tool description to make it crystal clear that the strings must be different:

```
"Edit a file by replacing text. CRITICAL: old_string and new_string MUST be different. 
The old_string must match exactly (including whitespace and indentation) and must be unique 
in the file unless replace_all is true. Include surrounding context (3-5 lines before and 
after) in old_string to ensure uniqueness."
```

Key additions:
- **CRITICAL** emphasizes the requirement
- Explains that surrounding context should be included
- This appears in the model's tool guidelines

### 5. **Improved Error Messages**
Replaced the generic error message with more actionable guidance:

**Before:**
```
"No change made - old_string equals new_string"
```

**After:**
```
"EDIT ERROR: old_string equals new_string - this is a no-op edit with no effect. 
Either: (1) Ensure new_string is actually different from old_string, 
(2) Re-read the file to verify the exact text you want to replace, or 
(3) Verify you're making the correct change."
```

### 6. **Updated Safety Check**
Kept the final safety check with improved messaging:

```python
# This should not occur due to early validation, but kept as safety check
if new_content == old_content:
    return ToolResult.error_result(
        "ERROR: Replacement resulted in no change. The old_string may not have been found, "
        "or old_string and new_string are identical."
    )
```

## Impact

These changes will:
1. **Prevent the error earlier** - caught at validation time, not after file operations
2. **Guide the model** - clear error messages explain what went wrong and how to fix it
3. **Improve tool description** - the model will see upfront that strings must be different
4. **Better user experience** - errors are shown in the preview before execution

## Testing

To verify the fix:
1. Attempt an edit with identical `old_string` and `new_string`
2. Verify you see the validation error with actionable guidance
3. The model should now understand to provide different strings

## Files Modified

- [tools/builtin/edit_file.py](tools/builtin/edit_file.py)
  - Added Pydantic field validator
  - Enhanced `execute()` method with early validation
  - Enhanced `get_confirmation()` method with early validation
  - Updated tool description
  - Improved error messages
