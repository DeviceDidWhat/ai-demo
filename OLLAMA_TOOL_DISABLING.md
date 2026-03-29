# Ollama Tool Disabling Implementation

## Overview
Implemented comprehensive tool disabling for Ollama models. When users select Ollama as their provider, they get chat-only capabilities with no tool function calls, even if explicitly requested.

## Changes Made

### 1. **LLMClient Tool Disabling** (`client/llm_client.py`)
Modified the LLMClient initialization to disable tools for Ollama upfront:

```python
from config.config import Config, Provider

class LLMClient:
    def __init__(self, config: Config) -> None:
        self._client: AsyncOpenAI | None = None
        self._max_retries: int = 3
        self.config = config
        # Ollama models do not support tool calling - disable it upfront
        self.tools_supported: bool = (config.provider != Provider.OLLAMA)
```

**Key Points:**
- Added import of `Provider` enum
- Changed `tools_supported` initialization from `True` to conditional check
- Now defaults to `False` when provider is `Provider.OLLAMA`
- Defaults to `True` for API providers

### 2. **System Prompt Information Section** (`prompts/system.py`)
Added Ollama limitations notice to the system prompt:

```python
def _get_ollama_limitations_section() -> str:
    """Generate limitations notice for Ollama models."""
    return """# IMPORTANT: Ollama Model Limitations

**You are running on a local Ollama model. The following capabilities are NOT available:**
- File operations (read_file, edit, write_file, glob, list_dir)
- Shell commands (shell)
- Web operations (web_search, web_fetch)
- Any other tool functions

**You are limited to chat-only interactions.** You cannot:
1. Execute any commands or tools even if explicitly asked by the user
2. Read, write, or modify files
3. Perform shell operations or system commands
4. Access the web or fetch external data

When a user asks you to perform any of these tasks, respond with:
"I'm unable to perform that task. I'm running on a local Ollama model which is chat-only and doesn't support tool function calls. I can only provide explanations, advice, and analysis through conversation. To use file operations or shell commands, you would need to use an API-based model provider."

Focus on providing helpful explanations and guidance instead."""
```

### 3. **System Prompt Integration** (`prompts/system.py`)
Updated `get_system_prompt()` to include the Ollama limitations section:

```python
def get_system_prompt(
    config: Config,
    user_memory: str | None = None,
    tools: list[Tool] | None = None,
) -> str:
    parts = []

    # Identity and role
    parts.append(_get_identity_section())
    # Environment
    parts.append(_get_environment_section(config))

    # Add tool limitations notice for Ollama
    if config.provider == Provider.OLLAMA:
        parts.append(_get_ollama_limitations_section())
    
    if tools:
        parts.append(_get_tool_guidelines_section(tools))
    
    # ... rest of prompt sections
```

**Key Points:**
- Checks `config.provider == Provider.OLLAMA`
- Only adds the limitations section for Ollama
- Placed before tool guidelines so model sees it clearly

## Behavior After Changes

### For API Providers (unchanged)
✓ Full tool support  
✓ File operations available  
✓ Shell commands available  
✓ Web operations available  
✓ All function calls enabled  

### For Ollama Providers (NEW)
✗ **NO tool support at all**  
✗ File operations disabled  
✗ Shell commands disabled  
✗ Web operations disabled  
✗ NO function calls allowed  

✓ Chat-only mode enabled  
✓ Model informed via system prompt  
✓ Graceful fallback prompts provided  

## How It Works - Flow Diagram

```
User selects Ollama provider
    ↓
Config.provider = Provider.OLLAMA
    ↓
LLMClient.__init__() called
    ↓
tools_supported = (config.provider != Provider.OLLAMA)
    ↓
tools_supported = False
    ↓
System prompt includes limitations section
    ↓
Agent._agentic_loop() called
    ↓
client.tools_supported == False
    ↓
Tool guidelines NOT injected in context
    ↓
tools parameter NOT sent to model
    ↓
Model responds with text only (no tool calls)
    ↓
If user asks for file/shell operations:
    ↓
Model responds with the provided fallback message
```

## User Experience

### When Using API Provider
```
User: "Read the config file and explain it"
Assistant: [executes read_file tool] [explains content]
```

### When Using Ollama Provider
```
User: "Read the config file and explain it"
Assistant: "I'm unable to perform that task. I'm running on a local 
Ollama model which is chat-only and doesn't support tool function calls. 
I can only provide explanations, advice, and analysis through conversation. 
To use file operations or shell commands, you would need to use an 
API-based model provider."
```

## Testing

✅ **Tool Support Detection**
- API provider: `tools_supported = True`
- Ollama provider: `tools_supported = False`

✅ **System Prompt Verification**
- API provider: No Ollama limitations section
- Ollama provider: Ollama limitations section present
- Ollama prompt includes: "chat-only", "not available", fallback message

✅ **Syntax Validation**
- All files compile without errors
- No import issues

## Files Modified

1. [client/llm_client.py](client/llm_client.py)
   - Added Provider import
   - Modified `tools_supported` initialization logic

2. [prompts/system.py](prompts/system.py)
   - Added Provider import
   - Added `_get_ollama_limitations_section()` function
   - Modified `get_system_prompt()` to conditionally include limitations section

## Backward Compatibility

✓ **Non-breaking changes:**
- API provider behavior unchanged
- Default behavior (API) unchanged
- Only affects Ollama provider selection
- Existing code continues to work

## Security & Safety

✓ **Benefits:**
- Ollama models cannot accidentally call tools
- Clear messaging to users about limitations
- Prevents confusion about capabilities
- Graceful degradation to chat-only mode

## Future Considerations

Possible enhancements:
1. Add configuration flag to allow tool enabling for Ollama (if desired)
2. Log warnings when Ollama tools are disabled
3. Add telemetry to track provider usage
4. Provide guidance for local tool execution via chat instructions

## Summary

The implementation ensures that:
1. Ollama models **CANNOT** call tools (disabled at LLMClient level)
2. Ollama users are **CLEARLY INFORMED** via system prompt
3. Models have **EXPLICIT FALLBACK MESSAGES** to explain limitations
4. API providers **REMAIN UNCHANGED** and fully functional
5. The architecture **REMAINS CLEAN** with minimal changes
