# AI Coding Agent

A sophisticated terminal-based AI coding assistant that provides an interactive CLI interface for software development tasks. This agent can read files, execute shell commands, edit code, search codebases, and more, all while maintaining context and providing a rich user experience.

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

This AI coding agent is a Python-based terminal application that acts as an intelligent pair programmer. It uses Large Language Models (LLMs) to understand natural language requests and autonomously executes tasks using a comprehensive tool system. The agent maintains conversation context, handles token limits through intelligent compression, and provides safety features like approval workflows for dangerous operations.

**Key Capabilities:**
- Interactive CLI with rich text formatting
- File operations (read, write, edit with diff preview)
- Shell command execution
- Codebase search (grep, glob, list directories)
- Web search and fetch capabilities
- Session persistence and checkpoints
- Hook system for custom workflows
- MCP (Model Context Protocol) server integration
- Loop detection and error recovery
- Context compression for long conversations

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
│   (agent/agent.py, agent/session.py)   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         LLM Client Layer                │
│   (client/llm_client.py)                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Tool System                     │
│   (tools/*, context/*)                  │
└─────────────────────────────────────────┘
```

---

## Project Structure

```
ai-coding-agent/
├── main.py                    # Entry point, CLI implementation
├── agent/
│   ├── agent.py              # Core agentic loop logic
│   ├── session.py            # Session management
│   ├── events.py             # Event types for agent lifecycle
│   └── persistence.py        # Session save/load functionality
├── client/
│   ├── llm_client.py         # OpenAI-compatible API client
│   └── response.py           # Response parsing and types
├── config/
│   ├── config.py             # Configuration models (Pydantic)
│   └── loader.py             # Config file loading
├── context/
│   ├── manager.py            # Conversation context management
│   ├── compaction.py         # Context compression
│   └── loop_detector.py      # Detects repetitive patterns
├── tools/
│   ├── base.py               # Base tool class and types
│   ├── registry.py           # Tool registration and invocation
│   ├── discovery.py          # Custom tool discovery
│   ├── subagents.py          # Sub-agent tools
│   ├── builtin/              # Built-in tools
│   │   ├── read_file.py
│   │   ├── write_file.py
│   │   ├── edit_file.py
│   │   ├── shell.py
│   │   ├── glob.py
│   │   ├── grep.py
│   │   ├── list_dir.py
│   │   ├── todo.py
│   │   ├── memory.py
│   │   ├── web_search.py
│   │   └── web_fetch.py
│   └── mcp/                  # MCP server integration
│       ├── mcp_manager.py
│       ├── client.py
│       └── mcp_tool.py
├── prompts/
│   └── system.py             # System prompt generation
├── safety/
│   └── approval.py           # Safety policies and approval workflows
├── hooks/
│   └── hook_system.py        # Event hooks for custom workflows
├── ui/
│   └── tui.py                # Terminal UI with Rich library
└── utils/
    ├── errors.py             # Custom error types
    ├── paths.py              # Path utilities
    └── text.py               # Text processing utilities
```

---

## Core Components

### 1. **main.py** - CLI Entry Point

The main entry point that provides both interactive and single-shot modes.

**Key Features:**
- **CLI Class**: Manages the overall application lifecycle
- **Interactive Mode**: Provides a REPL-style interface with command support
- **Single-shot Mode**: Execute a single prompt and exit
- **Command System**: Built-in slash commands for configuration and control

**Commands:**
- `/help` - Show help information
- `/exit` or `/quit` - Exit the agent
- `/clear` - Clear conversation history
- `/config` - Display current configuration
- `/model <name>` - Change the LLM model
- `/approval <mode>` - Change approval policy
- `/stats` - Show session statistics
- `/tools` - List available tools
- `/mcp` - Show MCP server status
- `/save` - Save current session
- `/sessions` - List saved sessions
- `/resume <id>` - Resume a saved session
- `/checkpoint` - Create a checkpoint
- `/restore <id>` - Restore from checkpoint

**Usage:**
```python
# Interactive mode
python main.py

# Single prompt mode
python main.py "Explain this codebase"
```

---

### 2. **agent/** - Agent Core

#### **agent/agent.py** - The Agentic Loop

The heart of the system that implements the autonomous agent behavior.

**Key Responsibilities:**
- Orchestrates the agentic loop (turn-based interaction)
- Streams LLM responses to the user
- Executes tool calls returned by the LLM
- Handles context compression when token limits are reached
- Implements loop detection to prevent infinite cycles
- Manages hooks (before/after agent execution)

**The Agentic Loop:**
```python
async def _agentic_loop(self):
    for turn_num in range(max_turns):
        # 1. Check if context compression is needed
        # 2. Get tool schemas from registry
        # 3. Call LLM with current context
        # 4. Stream response text to user
        # 5. Execute any tool calls
        # 6. Add tool results to context
        # 7. Check for infinite loops
        # 8. Continue until no more tool calls
```

**Key Methods:**
- `run(message)`: Main entry point for agent execution
- `_agentic_loop()`: Implements the turn-based execution loop

---

#### **agent/session.py** - Session Management

Manages the agent's session state and coordinates all subsystems.

**Components Managed:**
- `LLMClient`: API client for LLM communication
- `ToolRegistry`: All available tools
- `ContextManager`: Conversation history
- `MCPManager`: MCP server connections
- `ApprovalManager`: Safety approval system
- `LoopDetector`: Detects repetitive patterns
- `HookSystem`: Event hooks
- `ChatCompactor`: Context compression

**Key Features:**
- Session ID tracking with UUID
- Turn counting
- Statistics collection
- Memory loading (user preferences)
- Tool discovery on initialization

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

Handles communication with LLM APIs using the OpenAI SDK.

**Key Features:**
- Async streaming support
- Automatic retry logic with exponential backoff
- Error handling (rate limits, connection errors, API errors)
- Tool calling support (function calling)
- Both streaming and non-streaming modes

**Configuration:**
- Uses `API_KEY` environment variable
- Uses `BASE_URL` environment variable (supports OpenRouter, etc.)
- Configurable model name and temperature

**Streaming Process:**
1. Sends messages and tool schemas to API
2. Receives streaming chunks
3. Parses text deltas and tool call deltas
4. Yields events for text and tool calls
5. Returns usage statistics

---

### 4. **config/** - Configuration System

#### **config/config.py** - Configuration Models

Pydantic-based configuration system with validation.

**Main Models:**

**`Config`** - Root configuration
- `model`: ModelConfig (name, temperature, context window)
- `cwd`: Working directory
- `shell_environment`: Shell environment policies
- `hooks_enabled`: Enable/disable hooks
- `hooks`: List of hook configurations
- `approval`: Approval policy
- `max_turns`: Maximum agentic loop turns
- `mcp_servers`: MCP server configurations
- `allowed_tools`: Optional tool whitelist
- `developer_instructions`: Project-specific instructions
- `user_instructions`: User-specific instructions

**`ApprovalPolicy`** - Safety modes
- `ON_REQUEST`: Ask for approval before mutating operations (default)
- `ON_FAILURE`: Only ask if operation fails
- `AUTO`: Automatically approve safe operations
- `AUTO_EDIT`: Auto-approve edits, ask for shell commands
- `NEVER`: Block all mutating operations
- `YOLO`: Approve everything (dangerous)

**`MCPServerConfig`** - MCP server setup
- Supports stdio transport (command + args)
- Supports HTTP/SSE transport (URL)
- Per-server timeout configuration
- Environment variables for server process

---

#### **config/loader.py** - Configuration Loading

Loads configuration from multiple sources with precedence.

**Configuration Sources (in order of precedence):**
1. Project config: `.ai-agent/config.toml` in current directory
2. System config: `~/.config/ai-agent/config.toml`
3. AGENTS.md: Project-specific instructions in working directory

**Key Functions:**
- `load_config()`: Main entry point
- `get_config_dir()`: Returns `~/.config/ai-agent/`
- `get_data_dir()`: Returns `~/.local/share/ai-agent/`

---

### 5. **context/** - Context Management

#### **context/manager.py** - Context Manager

Manages the conversation history and token limits.

**Key Features:**
- Message tracking (user, assistant, tool, system)
- Token counting per message
- Context compression trigger (80% of context window)
- Tool output pruning (removes old tool outputs to save tokens)
- System prompt injection

**Message Types:**
- System: Initial instructions and prompts
- User: User messages
- Assistant: LLM responses (with optional tool calls)
- Tool: Tool execution results

**Pruning Strategy:**
- Protects last 40k tokens of tool outputs
- Prunes older tool outputs when exceeding threshold
- Replaces content with "[Old tool result content cleared]"
- Maintains tool call references for context

---

#### **context/compaction.py** - Context Compression

Compresses long conversations when approaching token limits.

**Compression Process:**
1. Formats conversation history for analysis
2. Sends to LLM with special compression prompt
3. Receives structured summary
4. Replaces conversation with summary + acknowledgment
5. Adds continuation prompt

**Summary Structure:**
- Original goal
- Completed actions (to avoid repetition)
- Current state
- In-progress work
- Remaining tasks
- Next step
- Key context

---

#### **context/loop_detector.py** - Loop Detection

Prevents the agent from getting stuck in repetitive patterns.

**Detection Methods:**
1. **Exact Repeats**: Same action repeated 3+ times
2. **Cycle Detection**: Repeating pattern of 2-3 actions

**Action Tracking:**
- Records tool calls with name and arguments
- Records text responses
- Maintains sliding window of last 20 actions
- Creates signature for each action

**Loop Breaking:**
- Injects special prompt when loop detected
- Asks agent to reflect and try different approach
- Prevents infinite execution

---

### 6. **tools/** - Tool System

#### **tools/base.py** - Base Tool Class

Abstract base class for all tools with common functionality.

**Key Classes:**

**`Tool`** (ABC)
- `name`: Tool identifier
- `description`: What the tool does
- `kind`: Tool type (read, write, shell, network, memory, mcp)
- `schema`: Pydantic model or dict for parameters
- `execute()`: Main execution method (async)
- `validate_params()`: Parameter validation
- `is_mutating()`: Whether tool changes state
- `get_confirmation()`: Returns confirmation info for approval
- `to_openai_schema()`: Converts to OpenAI function calling format

**`ToolResult`**
- `success`: Boolean indicating success/failure
- `output`: String output for the LLM
- `error`: Optional error message
- `metadata`: Additional structured data
- `diff`: Optional file diff
- `exit_code`: For shell commands
- `truncated`: Whether output was truncated

**`ToolKind`** - Tool categories
- `READ`: Non-mutating file/system reads
- `WRITE`: File writes and edits
- `SHELL`: Shell command execution
- `NETWORK`: Web requests
- `MEMORY`: Persistent memory storage
- `MCP`: MCP server tools

---

#### **tools/registry.py** - Tool Registry

Central registry for tool registration and invocation.

**Key Features:**
- Tool registration (builtin + MCP + custom)
- Tool lookup by name
- Schema generation for LLM function calling
- Tool invocation with approval checks
- Hook integration (before/after tool execution)
- Parameter validation

**Tool Filtering:**
- Optional whitelist via `allowed_tools` config
- Automatic filtering based on approval policies

**Invocation Flow:**
```python
async def invoke(name, params, cwd, hook_system, approval_manager):
    # 1. Get tool from registry
    # 2. Validate parameters
    # 3. Trigger before_tool hook
    # 4. Check approval if mutating
    # 5. Execute tool
    # 6. Trigger after_tool hook
    # 7. Return result
```

---

#### **tools/builtin/** - Built-in Tools

**File Operations:**

1. **read_file.py**: Read file contents with line range support
   - Supports offset and limit for large files
   - Returns content with line numbers
   - Metadata: shown range, total lines

2. **write_file.py**: Create new files or overwrite existing ones
   - Optional directory creation
   - Returns file diff
   - Safety: Requires approval for writes

3. **edit_file.py**: Surgical file edits with search/replace
   - Exact string matching
   - Optional replace-all mode
   - Shows before/after diff
   - Safety: Must read file first

**Search & Discovery:**

4. **glob.py**: File search by pattern
   - Unix-style glob patterns (`*.py`, `**/*.js`)
   - Returns sorted file paths
   - Metadata: match count

5. **grep.py**: Content search with ripgrep
   - Full regex support
   - Case-insensitive option
   - Context lines (-A, -B, -C)
   - File type filtering
   - Multiple output modes (content, files, count)

6. **list_dir.py**: Directory listing
   - Optional hidden file inclusion
   - File/directory distinction
   - Sorted output
   - Metadata: entry count

**Execution:**

7. **shell.py**: Execute shell commands
   - Configurable timeout (default 2 minutes)
   - Environment variable filtering (blocks secrets)
   - Captures stdout/stderr
   - Returns exit code
   - Safety: Dangerous command detection

**Task Management:**

8. **todo.py**: Task tracking system
   - Create/update/complete/delete todos
   - Persistent storage in session data
   - Supports markdown output
   - Helps agent track multi-step tasks

**Memory:**

9. **memory.py**: User preference storage
   - Key-value storage
   - Persistent across sessions
   - Operations: set, get, delete, list
   - Storage: `~/.local/share/ai-agent/user_memory.json`

**Web:**

10. **web_search.py**: Web search via Tavily API
    - Returns search results
    - Domain filtering
    - Configurable result count

11. **web_fetch.py**: Fetch web content
    - HTTP GET requests
    - HTML to markdown conversion
    - Caching support
    - Timeout handling

---

#### **tools/discovery.py** - Custom Tool Discovery

Discovers and loads custom tools from `.ai-agent/tools/` directories.

**Discovery Process:**
1. Scans project `.ai-agent/tools/` directory
2. Scans system config `.ai-agent/tools/` directory
3. Loads Python files
4. Finds Tool subclasses
5. Instantiates and registers tools

**Custom Tool Requirements:**
- Must inherit from `Tool` base class
- Must be in `.ai-agent/tools/*.py` file
- Must implement `execute()` method

---

#### **tools/mcp/** - MCP Integration

Model Context Protocol (MCP) support for external tool servers.

**Components:**

1. **mcp_manager.py**: MCP server lifecycle
   - Initializes MCP servers from config
   - Parallel connection with timeout
   - Tool registration
   - Shutdown handling

2. **client.py**: MCP protocol client
   - Stdio and HTTP/SSE transport support
   - Tool discovery via MCP protocol
   - Tool execution via MCP

3. **mcp_tool.py**: MCP tool wrapper
   - Wraps MCP tools as native tools
   - Parameter conversion
   - Result formatting

**Configuration Example:**
```toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
```

---

### 7. **prompts/** - System Prompts

#### **prompts/system.py** - Prompt Generation

Generates comprehensive system prompts for the LLM.

**Prompt Sections:**
1. **Identity**: Who the agent is and what it can do
2. **Environment**: OS, date, working directory, shell
3. **Tool Guidelines**: Available tools and usage patterns
4. **AGENTS.md Spec**: Project instruction file system
5. **Security Guidelines**: Safety rules
6. **Developer Instructions**: From AGENTS.md files
7. **User Instructions**: Custom user preferences
8. **Memory**: Remembered user preferences
9. **Operational Guidelines**: Coding standards and workflows

**Special Prompts:**
- `get_compression_prompt()`: For context compression
- `create_loop_breaker_prompt()`: For loop detection

---

### 8. **safety/** - Safety System

#### **safety/approval.py** - Approval Manager

Implements safety policies for mutating operations.

**Safety Features:**
- Command safety assessment
- Dangerous pattern detection
- Safe command patterns
- Path validation (must be in CWD)
- User confirmation flow

**Dangerous Patterns Detected:**
- File system destruction (`rm -rf /`)
- Disk operations (`dd`, `mkfs`)
- System control (`shutdown`, `reboot`)
- Permission changes on root
- Network exposure (`nc -l`)
- Code execution from network (`curl | bash`)
- Fork bombs

**Safe Command Patterns:**
- Information commands (`ls`, `cat`, `echo`)
- Read-only git commands (`git status`, `git log`)
- Read-only package managers
- Text processing tools
- System info commands

**Approval Flow:**
1. Check if operation is mutating
2. If command, assess safety patterns
3. Check approval policy
4. Validate affected paths
5. Request user confirmation if needed

---

### 9. **hooks/** - Hook System

#### **hooks/hook_system.py** - Event Hooks

Allows custom scripts/commands to run at specific points in execution.

**Hook Triggers:**
- `BEFORE_AGENT`: Before agent processes user message
- `AFTER_AGENT`: After agent completes response
- `BEFORE_TOOL`: Before any tool execution
- `AFTER_TOOL`: After tool completes
- `ON_ERROR`: When errors occur

**Hook Types:**
- **Command**: Execute a shell command
- **Script**: Execute a bash script file

**Environment Variables Provided:**
- `AI_AGENT_TRIGGER`: Hook trigger type
- `AI_AGENT_CWD`: Working directory
- `AI_AGENT_TOOL_NAME`: Tool being executed (if applicable)
- `AI_AGENT_TOOL_PARAMS`: JSON-encoded parameters
- `AI_AGENT_TOOL_RESULT`: Tool result
- `AI_AGENT_USER_MESSAGE`: User's message
- `AI_AGENT_RESPONSE`: Agent's response
- `AI_AGENT_ERROR`: Error message (if applicable)

**Use Cases:**
- Run tests before/after changes
- Trigger CI/CD pipelines
- Update documentation
- Log operations
- Custom validation

---

### 10. **ui/** - User Interface

#### **ui/tui.py** - Terminal UI

Rich text-based UI using the Rich library.

**Features:**
- Syntax highlighting for code
- Diff visualization
- Colored panels for tool execution
- Progress indicators
- Formatted output for each tool type
- Confirmation dialogs
- Help system

**Tool Output Formatting:**
- **read_file**: Syntax-highlighted code with line numbers
- **write_file/edit**: Diff view with context
- **shell**: Command echo + output + exit code
- **grep/glob**: Match counts and results
- **web_search/fetch**: URL and metadata
- **list_dir**: Entry counts
- **todos/memory**: Formatted lists

**Themes:**
- Cyan: Information, read operations
- Yellow: Write operations, warnings
- Magenta: Shell commands
- Green: Success, memory
- Red: Errors
- Blue: Network operations

---

## Configuration

### Environment Variables

Required:
```bash
export API_KEY="your-api-key"
export BASE_URL="https://api.openai.com/v1"  # or openrouter.ai, etc.
```

### Config File Format

**Location:** `.ai-agent/config.toml` (project) or `~/.config/ai-agent/config.toml` (system)

**Example:**
```toml
[model]
name = "mistralai/devstral-2512:free"
temperature = 0.7
context_window = 256000

approval = "on-request"
max_turns = 100
hooks_enabled = true

[shell_environment]
ignore_default_excludes = false
exclude_patterns = ["*KEY*", "*TOKEN*", "*SECRET*"]

[[hooks]]
name = "test_runner"
trigger = "after_tool"
command = "pytest tests/"
timeout_sec = 300
enabled = true

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path"]

[mcp_servers.web]
url = "http://localhost:3000/sse"
```

---

## Features

### 1. **Intelligent File Operations**
- Read files with line range support
- Surgical edits with diff preview
- Write new files with directory creation
- Automatic backup via diffs

### 2. **Powerful Search**
- Regex-based content search (ripgrep)
- Glob pattern file search
- Directory listings
- Multi-file parallel searches

### 3. **Safe Shell Execution**
- Dangerous command detection
- Environment variable filtering
- Timeout protection
- Approval workflows

### 4. **Context Management**
- Automatic context compression
- Tool output pruning
- Token counting
- Session persistence

### 5. **Loop Detection**
- Detects exact repeats
- Detects cyclic patterns
- Automatic intervention
- Prevents infinite loops

### 6. **MCP Integration**
- Connect to external tool servers
- Dynamic tool discovery
- Parallel server initialization
- Graceful error handling

### 7. **Hook System**
- Custom workflow automation
- Test runners
- CI/CD integration
- Event-driven execution

### 8. **Session Management**
- Save/resume sessions
- Checkpoint system
- Statistics tracking
- Usage monitoring

### 9. **Rich UI**
- Syntax highlighting
- Diff visualization
- Progress indicators
- Formatted tool output

### 10. **Memory System**
- User preference storage
- Cross-session persistence
- Key-value storage
- Automatic loading

---

## Installation & Usage

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-coding-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_KEY="your-api-key"
export BASE_URL="https://openrouter.ai/api/v1"

# Run
python main.py
```

### Basic Usage

**Interactive mode:**
```bash
python main.py
```

**Single prompt:**
```bash
python main.py "Explain how the agent loop works"
```

**With custom working directory:**
```bash
python main.py --cwd /path/to/project
```

### Configuration

Create `.ai-agent/config.toml` in your project:
```toml
[model]
name = "anthropic/claude-3.5-sonnet"
temperature = 0.7

approval = "auto-edit"
```

Create `AGENTS.md` for project-specific instructions:
```markdown
# Project Instructions

- Use 4 spaces for indentation
- Run `npm test` to test changes
- Follow ESLint configuration
```

### Custom Tools

Create `.ai-agent/tools/my_tool.py`:
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

---

## Summary

This AI coding agent is a comprehensive, production-ready system for AI-assisted software development. It combines:

- **Robust architecture** with clear separation of concerns
- **Extensive tool system** for file operations, search, and execution
- **Safety features** including approval workflows and dangerous command detection
- **Context management** with compression and pruning
- **Extensibility** via custom tools, hooks, and MCP servers
- **Rich user experience** with formatted output and real-time feedback
- **Session persistence** for long-running tasks
- **Error recovery** with loop detection and retry logic

The codebase is well-structured, uses modern Python practices (async/await, type hints, Pydantic), and provides a solid foundation for building AI-powered development tools.
