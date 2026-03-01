# Multi-Turn Tool Execution Issue - Root Cause Analysis & Fixes

## Problem 1: Tool Execution Fails After First Prompt

**Symptom:** Second prompt fails to execute tools; raw `<tool_call>` tags are displayed.

**Root Cause:** Type mismatch in tool call argument handling:
- Arguments were being converted to string representations with single quotes (invalid JSON)
- On the second turn, the invalid JSON in context caused parsing to fail
- Tool calls were silently skipped, displaying raw tags

**Fix:** Ensured arguments are consistently stored as valid JSON strings throughout the pipeline.

## Problem 2: Tool Is Called Repeatedly In A Loop

**Symptom:** After executing a tool like `read_file`, the agent keeps calling it again instead of providing the explanation.

**Root Cause:** Multiple issues:
1. Model instructions after tool execution were too vague ("Continue based on these results")
2. Loop detection threshold (3 repeats) was too high, allowing repeated calls
3. No mechanism to prevent duplicate tool calls within a single agent turn
4. Model continued generating identical tool calls due to unclear instructions

**Fixes:**

### 1. Enhanced Prompt-Based Tool Instructions (`prompts/system.py`)
Added explicit rules:
- "IMPORTANT: Only call each tool ONCE per request. Do NOT call the same tool multiple times in a row."
- "IMPORTANT: After you complete tool calls, ALWAYS provide analysis, explanation, or response text based on the tool results."

### 2. Improved Post-Tool-Execution Message (`agent/agent.py`)
Changed from vague "Continue based on these results" to:
```
"Tool execution complete. Here are the results: [results]

Based on these results, please provide your analysis, explanation, or response. 
Do NOT call the same tool again - instead, analyze the results and answer the user's question."
```

### 3. Duplicate Tool Call Detection Within Turn (`agent/agent.py`)
Added logic to:
- Create a hash signature of each tool call (tool name + arguments)
- Track executed tool calls within the current turn
- Skip and error out if the same tool with identical arguments is called again
- Send error message to model to avoid confusion

### 4. Aggressive Loop Detection (`context/loop_detector.py`)
- Reduced `max_exact_repeats` from 3 to 2 for faster loop detection
- Fixed typo: "tiems" → "times"
- Triggers loop-breaking prompt after just 2 repeated identical actions

## Files Modified

1. **`client/tool_parser.py`** - Fixed JSON serialization of arguments
2. **`client/llm_client.py`** - Ensured native tool calls use JSON strings for arguments  
3. **`agent/agent.py`** - Proper JSON parsing, duplicate detection, improved messages
4. **`prompts/system.py`** - Enhanced tool calling instructions with explicit rules
5. **`context/loop_detector.py`** - Improved loop detection, fixed typo

## How It Works Now

### First Prompt: Execute Tool
1. Model receives user request and tool instructions
2. Model outputs: `<tool_call>{"name": "read_file", "arguments": {"path": "file.cpp"}}</tool_call>`
3. Tool is executed successfully
4. Result added to context with explicit instruction not to repeat

### Second Prompt: Analyze & Respond
1. Model receives: tool result + "Do NOT call the same tool again" instruction
2. Model now provides analysis and explanation instead of repeating the tool call
3. If model tries to repeat anyway:
   - **Within turn:** Duplicate detector catches it → sends error
   - **Across turns:** Loop detector catches it after 2 attempts → sends loop-breaking prompt
4. Agent yields explanation as final response and exits

## Key Improvements

✅ First prompt: Tool calls executed correctly  
✅ Second prompt: Tool calls also executed correctly  
✅ No infinite loops of repeated tool calls  
✅ Clear error messages if duplicates are detected  
✅ Faster loop detection (2 repeats instead of 3)  
✅ Explicit instructions prevent tool call repetition  
✅ Consistent JSON handling throughout pipeline
