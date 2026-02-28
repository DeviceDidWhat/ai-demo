# AITAS - AI Coding Agent

A sophisticated terminal-based AI coding assistant that provides an interactive CLI interface for software development tasks. AITAS (AI Terminal Assistant) can read files, execute shell commands, edit code, search codebases, fetch web content, and more, all while maintaining context and providing a rich user experience with automatic context compression and safety features.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Configuration](#configuration)
- [Features](#features)
- [Installation & Usage](#installation--usage)

---

## Overview

AITAS is a Python-based terminal application that acts as an intelligent pair programmer. It uses Large Language Models (LLMs) through OpenAI-compatible APIs (including OpenRouter, local Ollama instances, and other providers) to understand natural language requests and autonomously executes tasks using a comprehensive tool system. The agent maintains conversation context, handles token limits through intelligent compression, and provides safety features like approval workflows for dangerous operations.

**Key Capabilities:**
- Interactive CLI with rich text formatting and syntax highlighting
- File operations (read, write, edit with diff preview)
- Shell command execution with safety checks
- Codebase search (grep with ripgrep, glob patterns, directory listings)
- Web search (via Tavily API) and web fetch capabilities
- Task management with TODO tracking
- Persistent memory system for user preferences
- Session persistence and checkpoint/restore functionality
- Hook system for custom workflows (run tests, CI/CD integration)
- MCP (Model Context Protocol) server integration
- Loop detection and error recovery
- Context compression for long conversations
- Support for both native tool calling and prompt-based tool calling
- Multi-provider support (OpenAI-compatible APIs and Ollama)

---

## Architecture

The application follows a layered architecture:

```
┌─────────────────────────────────────────┐
│         CLI / TUI Layer                 │
│   (main.py, ui/tui.py)                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Agent Layer                     │
│   (agent/agent.py, agent/session.py,   │
│    agent/events.py, agent/persistence.py│
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      LLM Client Layer                   │
│   (client/llm_client.py,                │
│    client/ollama.py,                    │
│    client/tool_parser.py)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Tool System & Context              │
│   (tools/*, context/*, safety/*,        │
│    hooks/*, prompts/*)                  │
└─────────────────────────────────────────┘
```

---

## Project Structure

```
ai-coding-agent/
├── main.py                    # Entry point, CLI implementation with interactive mode
├── agent/
│   ├── agent.py              # Core agentic loop logic and orchestration
│   ├── session.py            # Session management and subsystem coordination
│   ├── events.py             # Event types for agent lifecycle
│   └── persistence.py        # Session save/load and checkpoint functionality
├── client/
│   ├── llm_client.py         # OpenAI-compatible API client with streaming
│   ├── ollama.py             # Ollama server health checks and model listing
│   ├── response.py           # Response parsing and types (StreamEvent, ToolCall, etc.)
│   └── tool_parser.py        # Parse tool calls from text for non-native models
├── config/
│   ├── config.py             # Configuration models (Pydantic) with validation
│   └── loader.py             # Config file loading from multiple sources
├── context/
│   ├── manager.py            # Conversation context management and token tracking
│   ├── compaction.py         # Context compression via LLM summarization
│   └── loop_detector.py      # Detects repetitive patterns and cycles
├── tools/
│   ├── base.py               # Base tool class and types (Tool, ToolResult, ToolKind)
│   ├── registry.py           # Tool registration, lookup, and invocation
│   ├── discovery.py          # Custom tool discovery from .ai-agent/tools/
│   ├── subagents.py          # Sub-agent tools for complex tasks
│   ├── builtin/              # Built-in tools
│   │   ├── __init__.py
│   │   ├── read_file.py      # Read file with line ranges
│   │   ├── write_file.py     # Create/overwrite files
│   │   ├── edit_file.py      # Search and replace edits
│   │   ├── shell.py          # Execute shell commands
│   │   ├── glob.py           # File pattern matching
│   │   ├── grep.py           # Content search with ripgrep
│   │   ├── list_dir.py       # Directory listings
│   │   ├── todo.py           # Task tracking system
│   │   ├── memory.py         # Persistent user preferences
│   │   ├── web_search.py     # Tavily web search
│   │   └── web_fetch.py      # HTTP GET and HTML->Markdown
│   └── mcp/                  # MCP server integration
│       ├── mcp_manager.py    # MCP server lifecycle management
│       ├── client.py         # MCP protocol client (stdio/HTTP)
│       └── mcp_tool.py       # MCP tool wrapper
├── prompts/
│   └── system.py             # System prompt generation and special prompts
├── safety/
│   └── approval.py           # Safety policies and approval workflows
├── hooks/
│   └── hook_system.py        # Event hooks for custom workflows
├── ui/
│   └── tui.py                # Terminal UI with Rich library (syntax highlighting, diffs)
└── utils/
    ├── errors.py             # Custom error types
    ├── paths.py              # Path utilities (resolution, validation)
    └── text.py               # Text processing utilities (truncation, formatting)
```

---

## Core Components

### 1. **main.py** - CLI Entry Point

The main entry point that provides both interactive (REPL) and single-shot modes with keyboard interrupt handling.

**Key Features:**
- **CLI Class**: Manages the overall application lifecycle
- **Interactive Mode**: Provides a REPL-style interface with command support and Ctrl+C cancellation
- **Single-shot Mode**: Execute a single prompt and exit (`python main.py "your prompt"`)
- **Command System**: Built-in slash commands for configuration and control
- **Task Cancellation**: Gracefully handles Ctrl+C to cancel running agent tasks

**Commands:**
- `/help` - Show help information
- `/exit` or `/quit` - Exit the agent
- `/clear` - Clear conversation history
- `/config` - Display current configuration
- `/model <name>` - Change the LLM model
- `/approval <mode>` - Change approval policy (on-request, auto, auto-edit, yolo, never)
- `/stats` - Show session statistics (turns, token usage)
- `/tools` - List available tools
- `/mcp` - Show MCP server status
- `/save` - Save current session
- `/sessions` - List saved sessions
- `/resume <id>` - Resume a saved session
- `/checkpoint` - Create a checkpoint
- `/restore <id>` - Restore from checkpoint

**Usage:**
```bash
# Interactive mode
python main.py

# Single prompt mode
python main.py "Explain this codebase"

# With custom working directory
python main.py --cwd /path/to/project
```

**Provider Support:**
- **API Provider**: OpenAI-compatible APIs (OpenRouter, OpenAI, Anthropic via OpenRouter, etc.)
- **Ollama Provider**: Local Ollama instances with health checks and model listing

---

### 2. **agent/** - Agent Core

#### **agent/agent.py** - The Agentic Loop

The heart of the system that implements the autonomous agent behavior with support for both native and prompt-based tool calling.

**Key Responsibilities:**
- Orchestrates the agentic loop (turn-based interaction)
- Streams LLM responses to the user in real-time
- Executes tool calls returned by the LLM (native or parsed from text)
- Handles context compression when token limits are approached (80% threshold)
- Implements loop detection to prevent infinite cycles
- Manages hooks (before/after agent execution)
- Injects prompt-based tool instructions for models without native tool support

**The Agentic Loop:**
```python
async def _agentic_loop(self):
    for turn_num in range(max_turns):
        # 1. Check if context compression is needed (80% of context window)
        # 2. Inject tool instructions for non-native models
        # 3. Get tool schemas from registry
        # 4. Call LLM with current context (streaming)
        # 5. Stream response text to user (TEXT_DELTA events)
        # 6. Parse tool calls (native or from <tool_call> tags)
        # 7. Execute any tool calls via registry
        # 8. Add tool results to context
        # 9. Check for infinite loops (exact repeats or cycles)
        # 10. Continue until no more tool calls or max turns reached
```

**Key Methods:**
- `run(message)`: Main entry point for agent execution, yields AgentEvents
- `_agentic_loop()`: Implements the turn-based execution loop
- `_inject_prompt_based_tools()`: Adds tool calling instructions for non-native models
- `_execute_tool_calls()`: Executes tools and formats results
- `_loop_detected()`: Checks for repetitive patterns

**Event Streaming:**
The agent yields events throughout execution for reactive UI updates:
- `AGENT_START` / `AGENT_END`
- `TEXT_DELTA` / `TEXT_COMPLETE`
- `TOOL_CALL_START` / `TOOL_CALL_COMPLETE`
- `AGENT_ERROR`

---

#### **agent/session.py** - Session Management

Manages the agent's session state and coordinates all subsystems.

**Components Managed:**
- `LLMClient`: API client for LLM communication (OpenAI-compatible or Ollama)
- `ToolRegistry`: All available tools (builtin, MCP, and custom)
- `ContextManager`: Conversation history and token management
- `MCPManager`: MCP server connections and lifecycle
- `ApprovalManager`: Safety approval system with confirmation callbacks
- `LoopDetector`: Detects repetitive patterns and cycles
- `HookSystem`: Event hooks for custom workflows
- `ChatCompactor`: Context compression via LLM summarization

**Key Features:**
- Session ID tracking with UUID
- Turn counting for agentic loop iterations
- Statistics collection (tool calls, tokens used, turns)
- Memory loading from persistent storage (user preferences)
- Tool discovery on initialization (builtin + MCP + custom)
- Provider-specific client initialization (API or Ollama)

---

#### **agent/events.py** - Event System

Defines event types for the agent lifecycle to enable reactive UI updates.

**Event Types:**
- `AGENT_START` / `AGENT_END`: Agent execution lifecycle
- `TOOL_CALL_START` / `TOOL_CALL_COMPLETE`: Tool execution
- `TEXT_DELTA` / `TEXT_COMPLETE`: Streaming text responses
- `AGENT_ERROR`: Error conditions

---

#### **agent/persistence.py** - Session Persistence

Handles saving and loading of agent sessions for resumption.

**Classes:**
- `SessionSnapshot`: Dataclass representing a saved session
- `PersistenceManager`: Manages session and checkpoint files

**Features:**
- Session save/load with full conversation history
- Checkpoint system for creating restore points
- Secure file permissions (0o600 for files, 0o700 for directories)
- JSON serialization of session data

**Storage Location:**
- Sessions: `~/.local/share/ai-agent/sessions/`
- Checkpoints: `~/.local/share/ai-agent/checkpoints/`

---

### 3. **client/** - LLM Client

#### **client/llm_client.py** - OpenAI-Compatible Client

Handles communication with LLM APIs using the OpenAI SDK with comprehensive error handling.

**Key Features:**
- Async streaming support for real-time responses
- Automatic retry logic with exponential backoff (3 retries)
- Comprehensive error handling (rate limits, connection errors, API errors)
- Native tool calling support (OpenAI function calling format)
- Both streaming and non-streaming modes
- `tools_supported` flag to detect native tool calling capability

**Configuration:**
- Uses `API_KEY` environment variable (required for API provider)
- Uses `BASE_URL` environment variable (supports OpenRouter, OpenAI, etc.)
- Configurable model name and temperature
- Model-specific behavior (e.g., o1 models don't support system messages or temperature)

**Streaming Process:**
1. Sends messages and tool schemas to API
2. Receives streaming chunks (deltas)
3. Parses text deltas and tool call deltas
4. Yields StreamEvents for text and tool calls
5. Returns usage statistics (prompt tokens, completion tokens, total tokens)

**Error Recovery:**
- Rate limit errors: Automatic retry with backoff
- Connection errors: Retry with exponential delay
- API errors: Graceful error propagation

---

#### **client/ollama.py** - Ollama Integration

Helper functions for Ollama server health checks and model discovery.

**Functions:**
- `check_ollama_running(base_url)`: Health check for Ollama server
- `list_ollama_models(base_url)`: Fetch available model names

**Usage:**
Used during startup to validate Ollama provider configuration and list available models for selection.

---

#### **client/tool_parser.py** - Text-based Tool Calling

Parses tool calls from model text output for models without native tool calling support.

**Format:**
Models are instructed to emit tool calls in their text response using:
```xml
<tool_call>
{"name": "tool_name", "arguments": {"param": "value"}}
</tool_call>
```

**Features:**
- Regex-based extraction of tool call blocks
- JSON parsing with error handling
- Conversion to ToolCall objects with generated call IDs
- Supports multiple tool calls in a single response
- `strip_tool_call_tags()`: Removes tool call tags from final output

**Use Case:**
Enables tool calling for models that don't support OpenAI's native function calling format (e.g., some open-source models via Ollama).

---

### 4. **config/** - Configuration System

#### **config/config.py** - Configuration Models

Pydantic-based configuration system with validation.

**Main Models:**

**`Config`** - Root configuration
- `provider`: Provider (API or OLLAMA)
- `model`: ModelConfig (name, temperature, context_window)
- `cwd`: Working directory (Path)
- `shell_environment`: ShellEnvironmentPolicy (env var filtering, custom vars)
- `hooks_enabled`: Enable/disable hooks (bool)
- `hooks`: List of HookConfig
- `approval`: ApprovalPolicy (safety mode)
- `max_turns`: Maximum agentic loop turns (default 100)
- `mcp_servers`: Dict of MCP server configurations
- `allowed_tools`: Optional tool whitelist (list[str])
- `developer_instructions`: Project-specific instructions from AGENTS.md
- `user_instructions`: User-specific instructions (str)

**`Provider`** - LLM Provider types
- `API`: OpenAI-compatible API (OpenRouter, OpenAI, etc.)
- `OLLAMA`: Local Ollama instance

**`ApprovalPolicy`** - Safety modes
- `ON_REQUEST`: Ask for approval before mutating operations (default, safest)
- `ON_FAILURE`: Only ask if operation fails
- `AUTO`: Automatically approve safe operations
- `AUTO_EDIT`: Auto-approve file edits, ask for shell commands (balanced)
- `NEVER`: Block all mutating operations (read-only mode)
- `YOLO`: Approve everything without asking (dangerous, no safety net)

**`MCPServerConfig`** - MCP server setup
- Supports **stdio transport**: `command` + `args` (e.g., npx, python script)
- Supports **HTTP/SSE transport**: `url` (e.g., http://localhost:3000/sse)
- Per-server timeout configuration (`startup_timeout_sec`)
- Environment variables for server process (`env`)
- Working directory for server process (`cwd`)
- Enable/disable flag (`enabled`)

**Validation:**
- Must have either `command` (stdio) or `url` (HTTP/SSE), not both
- Pydantic model validation ensures configuration correctness

---

#### **config/loader.py** - Configuration Loading

Loads configuration from multiple sources with precedence and merging.

**Configuration Sources (in order of precedence):**
1. **Project config**: `.ai-agent/config.toml` in current directory (highest priority)
2. **System config**: `~/.config/ai-agent/config.toml` (user-wide defaults)
3. **AGENTS.md**: Project-specific instructions in working directory (auto-loaded as developer_instructions)
4. **Environment variables**: `API_KEY`, `BASE_URL` (required for API provider)

**Directory Structure:**
- Config: `~/.config/ai-agent/`
- Data: `~/.local/share/ai-agent/` (sessions, checkpoints, memory)

**Key Functions:**
- `load_config(cwd)`: Main entry point, loads and merges configs
- `get_config_dir()`: Returns `~/.config/ai-agent/` (or Windows equivalent)
- `get_data_dir()`: Returns `~/.local/share/ai-agent/` (or Windows equivalent)
- `_load_toml(path)`: Loads and validates TOML configuration

---

### 5. **context/** - Context Management

#### **context/manager.py** - Context Manager

Manages the conversation history, token limits, and message tracking.

**Key Features:**
- Message tracking (system, user, assistant, tool)
- Token counting per message (using tiktoken)
- Context compression trigger at 80% of context window
- Tool output pruning (removes old tool outputs to save tokens)
- System prompt injection and supplementation
- Latest usage tracking for streaming responses

**Message Types:**
- **System**: Initial instructions and prompts (immutable)
- **User**: User messages
- **Assistant**: LLM responses (with optional tool calls)
- **Tool**: Tool execution results (prunable)

**Pruning Strategy:**
- Protects last 40k tokens of tool outputs (recent context)
- Prunes older tool outputs when exceeding threshold
- Replaces pruned content with "[Old tool result content cleared]"
- Maintains tool call references for context integrity

**Token Management:**
- Counts tokens using `tiktoken` (cl100k_base encoding)
- Tracks total tokens including system prompt
- Triggers compression at 80% of context window
- Reports current usage vs. total capacity

**Key Methods:**
- `add_user_message()`: Add user input
- `add_assistant_message()`: Add LLM response with optional tool calls
- `add_tool_results()`: Add tool execution results
- `needs_compression()`: Check if approaching token limit
- `replace_with_summary()`: Replace history with compression summary
- `prune_old_tool_outputs()`: Remove old tool results to save tokens

---

#### **context/compaction.py** - Context Compression

Compresses long conversations when approaching token limits using LLM-powered summarization.

**Compression Process:**
1. Formats conversation history for analysis (excludes system prompt)
2. Sends to LLM with special compression prompt (non-streaming)
3. Receives structured summary with key context
4. Replaces conversation with summary + acknowledgment + continuation prompt
5. Adds usage statistics for compression API call

**Summary Structure:**
- **Original goal**: User's initial request
- **Completed actions**: What has been done (to avoid repetition)
- **Current state**: Current project/task state
- **In-progress work**: Partially completed tasks
- **Remaining tasks**: What still needs to be done
- **Next step**: Immediate next action
- **Key context**: Important context to preserve

**Benefits:**
- Prevents hitting token limits
- Preserves task continuity
- Reduces API costs
- Enables long-running sessions
- Maintains conversation coherence

**Trigger:**
Automatically triggered by ContextManager when reaching 80% of context window capacity.

---

#### **context/loop_detector.py** - Loop Detection

Prevents the agent from getting stuck in repetitive patterns and infinite loops.

**Detection Methods:**
1. **Exact Repeats**: Same action repeated 3+ consecutive times
2. **Cycle Detection**: Repeating pattern of 2-3 actions in a cycle

**Action Tracking:**
- Records tool calls with name and arguments (normalized)
- Records text responses
- Maintains sliding window of last 20 actions
- Creates signature hash for each action for efficient comparison

**Loop Breaking:**
- Injects special prompt when loop detected
- Asks agent to reflect on why it's stuck
- Suggests trying a different approach
- Prevents infinite execution and wasted tokens

**Example Detection:**
- Detects: `read_file -> grep -> read_file -> grep -> read_file -> grep`
- Detects: `shell(ls) -> shell(ls) -> shell(ls)`
- Prevents: Endless search loops, repeated failed attempts

**Integration:**
Called after each turn in the agentic loop; if loop detected, system injects intervention message.

---

### 6. **tools/** - Tool System

#### **tools/base.py** - Base Tool Class

Abstract base class for all tools with common functionality and type definitions.

**Key Classes:**

**`Tool`** (ABC)
- `name`: Tool identifier (str)
- `description`: What the tool does (for LLM)
- `kind`: Tool type (ToolKind enum)
- `schema`: Pydantic model or dict for parameters
- `execute(invocation)`: Main execution method (async, must implement)
- `validate_params()`: Parameter validation using Pydantic
- `is_mutating()`: Whether tool changes state (based on kind)
- `get_confirmation()`: Returns ToolConfirmation info for approval dialogs
- `to_openai_schema()`: Converts to OpenAI function calling format

**`ToolResult`**
- `success`: Boolean indicating success/failure
- `output`: String output shown to the LLM
- `error`: Optional error message
- `metadata`: Additional structured data (dict)
- `diff`: Optional file diff for edit operations
- `exit_code`: For shell commands (int)
- `truncated`: Whether output was truncated (bool)

**Helper Methods:**
- `ToolResult.success_result()`: Quick success result
- `ToolResult.error_result()`: Quick error result

**`ToolInvocation`**
- `tool_name`: Name of tool being invoked
- `params`: Parameters dict
- `call_id`: Unique identifier for this invocation

**`ToolConfirmation`**
- `tool_name`: Name of tool
- `description`: What the tool does
- `affected_paths`: Files/directories affected
- `command`: Shell command (if applicable)
- `safety_assessment`: Safe/Risky/Dangerous
- `reason`: Why approval is needed

**`ToolKind`** (Enum) - Tool categories
- `READ`: Non-mutating file/system reads (auto-approved)
- `WRITE`: File writes and edits (requires approval based on policy)
- `SHELL`: Shell command execution (safety checked)
- `NETWORK`: Web requests (may require approval)
- `MEMORY`: Persistent memory storage (approved)
- `MCP`: MCP server tools (varies)

---

#### **tools/registry.py** - Tool Registry

Central registry for tool registration, lookup, and invocation with safety checks.

**Key Features:**
- Tool registration (builtin + MCP + custom)
- Tool lookup by name (case-sensitive)
- Schema generation for LLM function calling (OpenAI format)
- Tool invocation with approval checks and validation
- Hook integration (before/after tool execution)
- Parameter validation using Pydantic
- Error handling and result formatting

**Tool Filtering:**
- Optional whitelist via `allowed_tools` config (restricts available tools)
- Automatic filtering based on approval policies (e.g., NEVER blocks mutating tools)

**Invocation Flow:**
```python
async def invoke(name, params, cwd, hook_system, approval_manager):
    # 1. Get tool from registry (by name)
    # 2. Validate parameters (Pydantic)
    # 3. Trigger before_tool hook (if enabled)
    # 4. Check approval if mutating (safety check)
    # 5. Execute tool (async)
    # 6. Trigger after_tool hook (if enabled)
    # 7. Handle errors and format result
    # 8. Return ToolResult
```

**Key Methods:**
- `register(tool)`: Register a new tool
- `get(name)`: Get tool by name
- `get_tools()`: Get all registered tools
- `get_schemas()`: Get OpenAI function calling schemas
- `invoke()`: Execute a tool with full safety pipeline

---

#### **tools/builtin/** - Built-in Tools

**File Operations:**

1. **read_file.py**: Read file contents with line range support
   - Supports `offset` and `limit` for large files (pagination)
   - Returns content with line numbers for reference
   - Metadata: shown range, total lines
   - Auto-truncates very large files to prevent token overflow

2. **write_file.py**: Create new files or overwrite existing ones
   - Optional directory creation (creates parent dirs automatically)
   - Returns file diff showing what was written
   - Safety: Requires approval for writes based on policy
   - Validates paths are within CWD

3. **edit_file.py**: Surgical file edits with search/replace
   - Exact string matching (must read file first to know content)
   - Optional replace-all mode (multiple occurrences)
   - Shows before/after diff with context
   - Safety: Must read file first, requires approval
   - Prevents accidental overwrites

**Search & Discovery:**

4. **glob.py**: File search by pattern
   - Unix-style glob patterns (`*.py`, `**/*.js`, `src/**/*.ts`)
   - Returns sorted file paths relative to CWD
   - Metadata: match count
   - Useful for finding files by extension or path pattern

5. **grep.py**: Content search with ripgrep
   - Full regex support (uses ripgrep under the hood)
   - Case-insensitive option (`-i`)
   - Context lines options (`-A`, `-B`, `-C`)
   - File type filtering (`-t python`, `-t javascript`)
   - Multiple output modes: content (default), files-only, count-only
   - Fast search across entire codebase
   - Shows line numbers and context

6. **list_dir.py**: Directory listing
   - Optional hidden file inclusion
   - File/directory distinction (directories marked with `/`)
   - Sorted output (directories first, then files)
   - Metadata: entry count

**Execution:**

7. **shell.py**: Execute shell commands
   - Configurable timeout (default 2 minutes, prevents hanging)
   - Environment variable filtering (blocks secrets: *KEY*, *TOKEN*, *SECRET*)
   - Custom environment variables from config
   - Captures stdout/stderr (combined or separate)
   - Returns exit code
   - Safety: Dangerous command detection (rm -rf, dd, shutdown, etc.)
   - Path validation (must operate within CWD)

**Task Management:**

8. **todo.py**: Task tracking system
   - Operations: create, update, complete, delete, list
   - Persistent storage in session data
   - Supports markdown output for readability
   - Helps agent track multi-step tasks
   - Prevents forgetting task progress

**Memory:**

9. **memory.py**: User preference storage
   - Key-value storage (dict-based)
   - Persistent across sessions
   - Operations: set, get, delete, list
   - Storage: `~/.local/share/ai-agent/user_memory.json`
   - Auto-loaded into system prompt on session start
   - Use cases: coding style, preferences, frequently used patterns

**Web:**

10. **web_search.py**: Web search via Tavily API
    - Returns search results with titles, URLs, snippets
    - Domain filtering (restrict to specific domains)
    - Configurable result count (default 5)
    - Requires `TAVILY_API_KEY` environment variable

11. **web_fetch.py**: Fetch web content
    - HTTP GET requests with timeout
    - HTML to markdown conversion (readable for LLM)
    - Basic caching support (avoids repeated fetches)
    - Timeout handling (prevents hanging on slow sites)
    - Returns cleaned, formatted content

---

#### **tools/discovery.py** - Custom Tool Discovery

Discovers and loads custom tools from `.ai-agent/tools/` directories.

**Discovery Process:**
1. Scans project `.ai-agent/tools/` directory (if exists)
2. Scans system config `.ai-agent/tools/` directory (if exists)
3. Loads Python files (`*.py`)
4. Finds Tool subclasses using introspection
5. Instantiates and registers tools in registry

**Custom Tool Requirements:**
- Must inherit from `Tool` base class
- Must be in `.ai-agent/tools/*.py` file
- Must implement `execute()` method
- Must define `name`, `description`, `kind`, and `schema`

**Example Custom Tool:**
```python
from tools.base import Tool, ToolInvocation, ToolResult, ToolKind
from pydantic import BaseModel

class MyToolParams(BaseModel):
    input: str

class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    kind = ToolKind.READ

    @property
    def schema(self):
        return MyToolParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = MyToolParams(**invocation.params)
        # Do something with params.input
        return ToolResult.success_result(f"Result: {params.input}")
```

**Use Cases:**
- Project-specific tools (e.g., database queries, API calls)
- Custom integrations (e.g., Jira, Slack)
- Domain-specific utilities (e.g., data processing, deployment scripts)

---

#### **tools/mcp/** - MCP Integration

Model Context Protocol (MCP) support for external tool servers.

**Components:**

1. **mcp_manager.py**: MCP server lifecycle management
   - Initializes MCP servers from config (parallel startup)
   - Handles both stdio and HTTP/SSE transport
   - Tool discovery via MCP protocol (list_tools)
   - Wraps MCP tools as native Tool instances
   - Graceful shutdown on exit
   - Connection timeout handling (per-server configurable)

2. **client.py**: MCP protocol client
   - Stdio transport support (subprocess-based)
   - HTTP/SSE transport support (for remote servers)
   - Tool discovery via MCP list_tools RPC
   - Tool execution via MCP call_tool RPC
   - Error handling and timeout management
   - Connection lifecycle (initialize, close)

3. **mcp_tool.py**: MCP tool wrapper
   - Wraps MCP tools as native Tool instances
   - Converts between MCP and internal formats
   - Parameter conversion (JSON schema to Pydantic)
   - Result formatting (MCP result to ToolResult)
   - Preserves tool metadata (description, schema)

**Configuration Example:**
```toml
# Stdio transport (npm package)
[mcp_servers.filesystem]
enabled = true
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
startup_timeout_sec = 10

# HTTP/SSE transport (remote server)
[mcp_servers.web]
enabled = true
url = "http://localhost:3000/sse"
startup_timeout_sec = 5
```

**Benefits:**
- Extend tool capabilities without modifying code
- Use community MCP servers (filesystem, git, database, etc.)
- Build custom MCP servers in any language
- Isolate tool execution in separate processes

---

### 7. **prompts/** - System Prompts

#### **prompts/system.py** - Prompt Generation

Generates comprehensive system prompts for the LLM with context about the environment, tools, and guidelines.

**Prompt Sections:**
1. **Identity**: Who the agent is (AITAS) and what it can do
2. **Environment**: OS, date, working directory, shell type
3. **Tool Guidelines**: Available tools and usage patterns
4. **AGENTS.md Spec**: Explains the project instruction file system
5. **Security Guidelines**: Safety rules (path restrictions, env var filtering)
6. **Developer Instructions**: From AGENTS.md files (project-specific)
7. **User Instructions**: Custom user preferences from config
8. **Memory**: Remembered user preferences from persistent storage
9. **Operational Guidelines**: Coding standards, workflows, best practices

**Special Prompts:**
- `get_compression_prompt()`: For context compression (asks LLM to summarize)
- `create_loop_breaker_prompt(history)`: For loop detection (intervention message)
- `get_prompt_based_tool_instructions(tools)`: For models without native tool calling

**Dynamic Content:**
- Tool schemas and descriptions (dynamically generated)
- Memory preferences (loaded from storage)
- Developer instructions (from AGENTS.md)
- Environment details (OS-specific, date-aware)

**AGENTS.md System:**
- Project-level: `AGENTS.md` in working directory
- Package-level: `AGENTS.md` in subdirectories (auto-discovered)
- System-level: `~/.config/ai-agent/AGENTS.md` (user defaults)
- Provides context-specific instructions to the agent

---

### 8. **safety/** - Safety System

#### **safety/approval.py** - Approval Manager

Implements safety policies for mutating operations with command safety assessment.

**Safety Features:**
- Command safety assessment (Safe/Risky/Dangerous)
- Dangerous pattern detection (regex-based)
- Safe command patterns (allowlist)
- Path validation (must be within CWD, prevents escaping)
- User confirmation flow with Rich UI
- Approval policy enforcement

**Dangerous Patterns Detected:**
- **File system destruction**: `rm -rf /`, `rm -rf /*`, `del /s /q C:\`
- **Disk operations**: `dd`, `mkfs`, `format`
- **System control**: `shutdown`, `reboot`, `halt`, `poweroff`
- **Permission changes on root**: `chmod 777 /`, `chown * /`
- **Network exposure**: `nc -l`, `ncat -l` (listening ports)
- **Code execution from network**: `curl | bash`, `wget | sh`
- **Fork bombs**: `:(){ :|:& };:`
- **Package manager remove all**: `apt remove *`, `yum erase *`

**Safe Command Patterns (Auto-approved even in strict modes):**
- **Information commands**: `ls`, `cat`, `echo`, `pwd`, `which`, `type`
- **Read-only git commands**: `git status`, `git log`, `git diff`, `git show`
- **Read-only package managers**: `npm list`, `pip list`, `apt search`
- **Text processing tools**: `grep`, `awk`, `sed`, `sort`, `uniq`
- **System info commands**: `date`, `whoami`, `hostname`, `uname`

**Approval Flow:**
1. Check if operation is mutating (based on ToolKind)
2. If shell command, assess safety patterns (dangerous/risky/safe)
3. Check approval policy (ON_REQUEST, AUTO, AUTO_EDIT, etc.)
4. Validate affected paths (must be within CWD)
5. Request user confirmation if needed (via confirmation callback)
6. Allow or block operation

**Approval Policies:**
- `ON_REQUEST`: Ask for all mutating operations (safest)
- `AUTO`: Auto-approve safe operations, ask for risky/dangerous
- `AUTO_EDIT`: Auto-approve file edits, ask for shell commands
- `NEVER`: Block all mutating operations (read-only mode)
- `YOLO`: Approve everything (dangerous, no safety net)

---

### 9. **hooks/** - Hook System

#### **hooks/hook_system.py** - Event Hooks

Allows custom scripts/commands to run at specific points in execution for workflow automation.

**Hook Triggers:**
- `BEFORE_AGENT`: Before agent processes user message
- `AFTER_AGENT`: After agent completes response
- `BEFORE_TOOL`: Before any tool execution
- `AFTER_TOOL`: After tool completes
- `ON_ERROR`: When errors occur

**Hook Types:**
- **Command**: Execute a shell command (e.g., `pytest tests/`)
- **Script**: Execute a bash/shell script file (e.g., `./hooks/run_tests.sh`)

**Environment Variables Provided to Hooks:**
- `AI_AGENT_TRIGGER`: Hook trigger type (e.g., "after_tool")
- `AI_AGENT_CWD`: Working directory
- `AI_AGENT_TOOL_NAME`: Tool being executed (if applicable)
- `AI_AGENT_TOOL_PARAMS`: JSON-encoded parameters
- `AI_AGENT_TOOL_RESULT`: Tool result (JSON)
- `AI_AGENT_USER_MESSAGE`: User's message
- `AI_AGENT_RESPONSE`: Agent's response
- `AI_AGENT_ERROR`: Error message (if applicable)

**Configuration Example:**
```toml
hooks_enabled = true

[[hooks]]
name = "test_runner"
trigger = "after_tool"
command = "pytest tests/"
timeout_sec = 300
enabled = true

[[hooks]]
name = "linter"
trigger = "after_agent"
script = ".ai-agent/hooks/lint.sh"
timeout_sec = 60
enabled = true
```

**Use Cases:**
- **Run tests before/after changes**: Ensure code changes don't break tests
- **Trigger CI/CD pipelines**: Kick off builds or deployments
- **Update documentation**: Auto-generate docs after code changes
- **Log operations**: Audit trail for agent actions
- **Custom validation**: Run custom checks (security scans, linters)
- **Notifications**: Send alerts on errors or completions

---

### 10. **ui/** - User Interface

#### **ui/tui.py** - Terminal UI

Rich text-based UI using the Rich library for beautiful terminal output.

**Features:**
- Syntax highlighting for code (50+ languages)
- Diff visualization (unified diff format with colors)
- Colored panels for tool execution
- Progress indicators and spinners
- Formatted output for each tool type
- Confirmation dialogs with safety warnings
- Help system with command documentation
- Live streaming output during agent execution

**Tool Output Formatting:**
- **read_file**: Syntax-highlighted code with line numbers
- **write_file/edit_file**: Diff view with context (green additions, red deletions)
- **shell**: Command echo + output + exit code (color-coded by exit status)
- **grep/glob**: Match counts and results with highlighting
- **web_search/web_fetch**: URL and metadata in blue panels
- **list_dir**: Entry counts with directory/file distinction
- **todos/memory**: Formatted lists with structure
- **MCP tools**: Generic formatting with metadata

**Color Themes:**
- **Cyan**: Information, read operations
- **Yellow**: Write operations, warnings
- **Magenta**: Shell commands
- **Green**: Success, memory operations
- **Red**: Errors, dangerous operations
- **Blue**: Network operations (web search, fetch)
- **Dim**: Secondary information, metadata

**Confirmation Dialogs:**
- Shows tool name and description
- Lists affected paths
- Displays command (for shell operations)
- Safety assessment (Safe/Risky/Dangerous)
- Color-coded warnings (red for dangerous)
- Accept/Reject options

**Welcome Screen:**
- ASCII art banner
- Provider and model information
- Working directory
- Available commands

---

## Configuration

### Environment Variables

**Required for API Provider:**
```bash
export API_KEY="your-api-key"  # OpenAI, OpenRouter, Anthropic, etc.
export BASE_URL="https://api.openai.com/v1"  # Or https://openrouter.ai/api/v1
```

**Optional:**
```bash
export TAVILY_API_KEY="your-tavily-key"  # For web search tool
```

**For Ollama Provider:**
No API key needed. Ollama must be running locally at `http://localhost:11434` (default).

### Config File Format

**Location:** 
- Project: `.ai-agent/config.toml` (highest priority)
- System: `~/.config/ai-agent/config.toml` (user defaults)
- Windows: `%USERPROFILE%\.config\ai-agent\config.toml`

**Complete Example:**
```toml
# Provider: "api" or "ollama"
provider = "api"

# Model configuration
[model]
name = "mistralai/devstral-2512"  # Or "anthropic/claude-3.5-sonnet", "gpt-4o", etc.
temperature = 0.7
context_window = 256000

# Safety policy
approval = "auto-edit"  # Options: on-request, auto, auto-edit, yolo, never

# Max agentic loop iterations
max_turns = 100

# Enable hooks
hooks_enabled = true

# Shell environment filtering
[shell_environment]
ignore_default_excludes = false
exclude_patterns = ["*KEY*", "*TOKEN*", "*SECRET*", "*PASSWORD*"]

# Set custom environment variables
[shell_environment.set_vars]
NODE_ENV = "development"
PYTHON_ENV = "test"

# Hook configurations
[[hooks]]
name = "test_runner"
trigger = "after_tool"
command = "pytest tests/ -v"
timeout_sec = 300
enabled = true

[[hooks]]
name = "linter"
trigger = "after_agent"
script = ".ai-agent/hooks/lint.sh"
timeout_sec = 60
enabled = false

# MCP server configurations
[mcp_servers.filesystem]
enabled = true
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
startup_timeout_sec = 10

[mcp_servers.web]
enabled = false
url = "http://localhost:3000/sse"
startup_timeout_sec = 5

# Tool whitelist (optional, restricts available tools)
allowed_tools = ["read_file", "write_file", "edit_file", "shell", "grep", "glob"]

# Custom instructions
user_instructions = """
- Prefer functional programming
- Use type hints in Python
- Write comprehensive docstrings
"""
```

### AGENTS.md Files

Create `AGENTS.md` in your project root for project-specific instructions:

```markdown
# Project Instructions for AITAS

## Project Overview
This is a Python web application using Flask and PostgreSQL.

## Coding Standards
- Use 4 spaces for indentation
- Follow PEP 8 style guide
- Write type hints for all functions
- Use docstrings (Google style)

## Testing
- Run `pytest tests/` to test changes
- Maintain test coverage above 80%
- Write integration tests for new endpoints

## Development Workflow
1. Create feature branch from `main`
2. Make changes and write tests
3. Run `black .` to format code
4. Run `flake8` to check linting
5. Commit and push

## Important Files
- `app.py`: Main Flask application
- `models.py`: Database models
- `config.py`: Configuration
- `requirements.txt`: Dependencies

## Common Commands
- Start dev server: `flask run --debug`
- Run migrations: `flask db upgrade`
- Create migration: `flask db migrate -m "message"`
```

---

## Features

### 1. **Intelligent File Operations**
- Read files with line range support and pagination
- Surgical edits with exact search/replace and diff preview
- Write new files with automatic directory creation
- Automatic backup via diffs
- Syntax highlighting for 50+ languages

### 2. **Powerful Search**
- Regex-based content search powered by ripgrep
- Glob pattern file search with full wildcard support
- Directory listings with hidden file support
- Multi-file parallel searches
- Context lines and file type filtering

### 3. **Safe Shell Execution**
- Dangerous command detection (rm -rf, shutdown, etc.)
- Environment variable filtering (blocks secrets)
- Timeout protection (prevents hanging processes)
- Approval workflows with safety assessment
- Path validation (restricted to CWD)
- Exit code tracking and stderr capture

### 4. **Context Management**
- Automatic context compression at 80% threshold
- Tool output pruning (keeps last 40k tokens)
- Token counting with tiktoken
- Session persistence with full history
- Smart summarization preserving task continuity

### 5. **Loop Detection**
- Detects exact repeats (3+ consecutive)
- Detects cyclic patterns (2-3 action cycles)
- Automatic intervention with reflection prompts
- Prevents infinite loops and wasted tokens
- Sliding window of last 20 actions

### 6. **MCP Integration**
- Connect to external tool servers
- Dynamic tool discovery via MCP protocol
- Parallel server initialization with timeouts
- Support for stdio and HTTP/SSE transport
- Graceful error handling and shutdown

### 7. **Hook System**
- Custom workflow automation
- Test runners (pytest, jest, etc.)
- CI/CD integration
- Event-driven execution (before/after tool, agent)
- Environment variables passed to hooks

### 8. **Session Management**
- Save/resume sessions with full context
- Checkpoint system for restore points
- Statistics tracking (tokens, turns, tool calls)
- Usage monitoring and reporting
- Session persistence across restarts

### 9. **Rich UI**
- Syntax highlighting for code
- Diff visualization (unified format)
- Progress indicators and spinners
- Formatted tool output by type
- Color-coded safety warnings
- Live streaming output

### 10. **Memory System**
- User preference storage (key-value)
- Cross-session persistence
- Automatic loading into system prompt
- Operations: set, get, delete, list
- Storage: `~/.local/share/ai-agent/user_memory.json`

### 11. **Multi-Provider Support**
- OpenAI-compatible APIs (OpenRouter, OpenAI, Anthropic)
- Local Ollama support (no API key needed)
- Health checks and model listing
- Native and prompt-based tool calling
- Streaming responses

### 12. **Safety Features**
- Approval policies (6 modes from read-only to YOLO)
- Command safety assessment (Safe/Risky/Dangerous)
- Path validation (CWD restriction)
- Secret filtering from environment
- Confirmation callbacks with Rich UI

---

## Installation & Usage

### Prerequisites

- Python 3.10+ (3.11 or 3.12 recommended)
- `ripgrep` (for grep tool) - [Installation instructions](https://github.com/BurntSushi/ripgrep#installation)
- Optional: Ollama (for local LLM support) - [Installation instructions](https://ollama.ai)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-coding-agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_KEY="your-api-key"  # For API provider
export BASE_URL="https://openrouter.ai/api/v1"  # Or https://api.openai.com/v1

# Optional: For web search
export TAVILY_API_KEY="your-tavily-key"
```

### Basic Usage

**Interactive mode (recommended):**
```bash
python main.py

# Welcome screen appears
# Type your requests at the prompt:
# AITAS > Read the main.py file and explain how it works

# Use slash commands:
# AITAS > /help      # Show all commands
# AITAS > /tools     # List available tools
# AITAS > /config    # Show configuration
# AITAS > /exit      # Exit the agent
```

**Single prompt mode:**
```bash
python main.py "Explain how the agent loop works in agent.py"

# The agent will process the request and exit
# Useful for automation and scripting
```

**With custom working directory:**
```bash
python main.py --cwd /path/to/project
python main.py --cwd /path/to/project "Add error handling to the API"
```

**Command-line options:**
```bash
python main.py --help                    # Show help
python main.py --cwd PATH                # Set working directory
python main.py "prompt"                  # Single-shot mode
python main.py --provider ollama         # Use Ollama provider
python main.py --model "llama3"          # Set model name
```

### Configuration

**Create project configuration:**
```bash
mkdir -p .ai-agent
cat > .ai-agent/config.toml << EOF
provider = "api"

[model]
name = "anthropic/claude-3.5-sonnet"
temperature = 0.7

approval = "auto-edit"
max_turns = 100
EOF
```

**Create AGENTS.md for project instructions:**
```bash
cat > AGENTS.md << EOF
# Project Instructions

- Use 4 spaces for indentation
- Run \`npm test\` to test changes
- Follow ESLint configuration
- Write JSDoc comments for functions
EOF
```

### Custom Tools

Create custom tools in `.ai-agent/tools/`:

```bash
mkdir -p .ai-agent/tools
cat > .ai-agent/tools/my_tool.py << 'EOF'
from tools.base import Tool, ToolInvocation, ToolResult, ToolKind
from pydantic import BaseModel

class MyToolParams(BaseModel):
    message: str

class MyTool(Tool):
    name = "my_tool"
    description = "A custom tool that echoes a message"
    kind = ToolKind.READ

    @property
    def schema(self):
        return MyToolParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = MyToolParams(**invocation.params)
        return ToolResult.success_result(f"Echo: {params.message}")
EOF

python main.py
# Your custom tool will be automatically discovered and available
```

### Using Ollama (Local LLMs)

```bash
# Install Ollama: https://ollama.ai

# Pull a model
ollama pull llama3

# Update config
cat > .ai-agent/config.toml << EOF
provider = "ollama"

[model]
name = "llama3"
temperature = 0.7
context_window = 128000
EOF

# Run AITAS
python main.py
```

### Session Management

```bash
# In interactive mode:
AITAS > /save              # Save current session
AITAS > /sessions          # List saved sessions
AITAS > /resume <id>       # Resume a saved session

AITAS > /checkpoint        # Create checkpoint
AITAS > /restore <id>      # Restore from checkpoint
```

### Examples

**Example 1: Codebase exploration**
```bash
python main.py
AITAS > What files are in this project?
AITAS > Read the agent.py file and explain the agentic loop
AITAS > Search for all TODO comments in the codebase
```

**Example 2: Code refactoring**
```bash
python main.py
AITAS > Find all functions in src/ that are longer than 50 lines
AITAS > Refactor the parse_config function in config.py to be more modular
AITAS > Add type hints to all functions in utils.py
```

**Example 3: Testing and CI**
```bash
python main.py
AITAS > Run the tests with pytest and fix any failures
AITAS > Add a test for the new authentication feature
AITAS > Generate a GitHub Actions workflow for CI
```

**Example 4: Documentation**
```bash
python main.py
AITAS > Generate a README for this project based on the code
AITAS > Add docstrings to all public functions in api.py
AITAS > Create API documentation from the Flask routes
```

---

## Summary

AITAS (AI Terminal Assistant) is a comprehensive, production-ready system for AI-assisted software development. It combines:

- **Robust architecture** with clear separation of concerns (Agent, Client, Tools, UI layers)
- **Extensive tool system** for file operations, search, shell execution, web access, and more (11 built-in tools)
- **Multi-provider support** for OpenAI-compatible APIs and local Ollama instances
- **Safety features** including 6 approval policies, dangerous command detection, and path validation
- **Context management** with automatic compression at 80% threshold and intelligent pruning
- **Extensibility** via custom tools, hooks, and MCP server integration
- **Rich user experience** with syntax highlighting, diff visualization, and formatted output
- **Session persistence** with save/resume and checkpoint/restore functionality
- **Error recovery** with loop detection, retry logic, and intervention prompts
- **Workflow automation** through hooks for tests, CI/CD, and custom validation

**Technology Stack:**
- Python 3.10+ with modern async/await patterns
- Pydantic for configuration and validation
- Rich library for terminal UI
- OpenAI SDK for LLM communication
- Tiktoken for token counting
- Ripgrep for fast content search
- MCP protocol for external tool servers

**Key Differentiators:**
1. **Hybrid tool calling**: Supports both native and prompt-based tool calling for maximum model compatibility
2. **Intelligent context management**: Automatic compression and pruning prevents token limit issues
3. **Loop detection**: Prevents infinite cycles and wasted API calls
4. **Granular safety controls**: 6 approval policies from read-only to YOLO
5. **Hook system**: Automate workflows with custom scripts at key execution points
6. **MCP integration**: Extend capabilities through external tool servers
7. **Session persistence**: Resume long-running tasks across restarts
8. **Memory system**: Remember user preferences across sessions

The codebase is well-structured, uses modern Python practices (async/await, type hints, Pydantic models), follows SOLID principles, and provides a solid foundation for building AI-powered development tools. The modular design makes it easy to add new tools, extend functionality, and customize behavior for specific use cases.

**Perfect for:**
- Code exploration and documentation
- Automated refactoring and code improvements
- Test generation and debugging
- DevOps and deployment automation
- Learning new codebases
- Pair programming with AI
- Code review and quality assurance

---

**Project Status:** Production-ready, actively maintained

**License:** [Specify your license]

**Contributing:** [Specify contribution guidelines]

**Support:** [Specify support channels]
