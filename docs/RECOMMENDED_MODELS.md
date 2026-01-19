# Recommended Models for AI Coding Agent

## 🚨 IMPORTANT UPDATE - Ollama Tool Calling Issues

**As of January 2025 (Ollama v0.14.2):**
- Ollama's OpenAI-compatible API has **critical bugs** with tool calling
- All Ollama models fail with "invalid tool call arguments" errors
- **Ollama models can only run in basic chat mode** (no file operations, no code execution)

**For full coding features, use OpenAI API or compatible providers instead.**

---

## Quick Answer

**For FULL coding features (RECOMMENDED):**
```bash
# Use OpenAI API
python main.py
# Select "OpenAI API" → Enter API key → Use gpt-4o-mini or gpt-4o
```

**For local/chat-only mode (LIMITED):**
```bash
# Use Ollama (chat advice only, no actual code execution)
ollama pull llama3.2
python main.py
# Select "Ollama" → Any model (all run in chat-only mode)
```

## Why Tool Support Matters

This AI agent needs **tool calling** support to:
- Read and write files
- Execute shell commands
- Search code with grep
- Navigate directories
- Edit code
- Run tests
- And more...

Without tool support, the agent can only chat - it can't actually DO anything.

## ⚠️ Ollama Status (Chat-Only Mode)

**Current Limitation:** Ollama v0.14.2 has bugs in its OpenAI-compatible tool calling API.
All Ollama models currently run in **chat-only mode**:

- ✅ Can provide coding advice and suggestions
- ✅ Can explain code and answer questions
- ✅ Can generate code snippets
- ❌ Cannot read or write files
- ❌ Cannot execute commands
- ❌ Cannot make actual code changes

**These models work for chat, but pick any one:**

### Lightweight Models (2-5GB)

| Model | Size | Pull Command | Chat Quality |
|-------|------|--------------|--------------|
| **llama3.2:3b** | 2GB | `ollama pull llama3.2:3b` | Good, fast responses |
| **llama3.1:8b** | 4.7GB | `ollama pull llama3.1:8b` | Better reasoning |
| **mistral:7b** | 4.1GB | `ollama pull mistral:7b` | Good general purpose |
| **qwen2.5:7b** | 4.7GB | `ollama pull qwen2.5:7b` | Good for code |

### High Performance Models (8GB+)

| Model | Size | Pull Command | Chat Quality |
|-------|------|--------------|--------------|
| **qwen2.5:14b** | 9GB | `ollama pull qwen2.5:14b` | Better code understanding |
| **llama3.1:70b** | 40GB | `ollama pull llama3.1:70b` | Highest quality |

**Note:** All these models have the same limitation - chat-only mode. Pick based on your hardware and preferred model.

## ✅ OpenAI API Models (Full Tool Support)

All OpenAI models have **full tool support** - they can read, write, edit files, execute commands, and more.

### Recommended (Best Choice for Coding)

| Model | Cost | Quality | Best For |
|-------|------|---------|----------|
| **gpt-4o** | $$$ | Excellent | Complex coding tasks |
| **gpt-4o-mini** | $ | Very Good | ⭐ Best value - recommended |
| **gpt-4-turbo** | $$$ | Excellent | Large context needed |
| **gpt-3.5-turbo** | $ | Good | Budget option |

## ✅ OpenRouter Models (Full Tool Support)

Most models on OpenRouter have **full tool support**. Recommended:

| Model | Cost | Quality | Best For |
|-------|------|---------|----------|
| **anthropic/claude-3.5-sonnet** | $$ | Excellent | Complex reasoning, code |
| **google/gemini-pro-1.5** | $$ | Very Good | Large context tasks |
| **mistralai/mistral-large** | $$ | Very Good | General coding |
| **mistralai/devstral-2512:free** | FREE | Good | Budget option (free!) |

## Quick Setup Examples

### Example 1: Full Coding Features (RECOMMENDED)

```bash
python main.py

# Interactive selection:
# 1. Select: OpenAI API
# 2. Enter your API key
# 3. Choose provider: OpenAI
# 4. Model: gpt-4o-mini (or gpt-4o)

# Now you can use ALL features:
# - File operations
# - Code execution
# - Shell commands
```

### Example 2: Free OpenRouter (Full Features)

```bash
python main.py

# Interactive selection:
# 1. Select: OpenAI API
# 2. Get free key from: https://openrouter.ai/keys
# 3. Choose provider: OpenRouter
# 4. Model: mistralai/devstral-2512:free

# Full tool support, completely free!
```

### Example 3: Local Chat-Only (LIMITED)

```bash
# Only for advice/explanations, not actual coding
ollama pull llama3.2:3b
python main.py

# Select: Ollama → llama3.2:3b
# Will only provide chat responses, no file operations
```

## Testing Your Model

After starting the agent, test if tools work:

```
User: Create a file called test.txt with "hello world"
```

**✅ Working (with tools):**
```
[Tool Call] write_file(file_path="test.txt", content="hello world")
[Success] File created
```

**❌ Not Working (without tools):**
```
Here's how you could create that file:
```bash
echo "hello world" > test.txt"
```
(No actual file is created)
```

## Troubleshooting

### Problem: "invalid tool call arguments" error with Ollama

**Cause:** Ollama v0.14.2 has bugs in tool calling API

**Solution:** This is expected. Options:
1. Continue using Ollama in chat-only mode (no file operations)
2. Switch to OpenAI API for full features:
   ```bash
   python main.py
   # Select: OpenAI API → Enter key → gpt-4o-mini
   ```

### Problem: Agent just describes actions but doesn't execute them (Ollama)

**Cause:** Ollama runs in chat-only mode due to tool calling bugs

**Solution:** Use OpenAI API or OpenRouter for actual file operations:
```bash
python main.py
# Select: OpenAI API
```

### Problem: Need full features but don't want to pay

**Solution:** Use OpenRouter's free tier:
```bash
# Get free API key from https://openrouter.ai/keys
python main.py
# Select: OpenAI API
# Choose: OpenRouter
# Model: mistralai/devstral-2512:free
```

## Hardware Requirements

| Model | Minimum RAM | Recommended GPU |
|-------|-------------|-----------------|
| llama3.2 (2GB) | 8GB | Not needed |
| mistral (4GB) | 16GB | 4GB+ VRAM helps |
| qwen2.5:7b (5GB) | 16GB | 6GB+ VRAM |
| llama3.1:8b (5GB) | 16GB | 6GB+ VRAM |
| mixtral (26GB) | 32GB+ | 16GB+ VRAM required |

## Summary & Recommendation

### 🏆 BEST CHOICE (Full Features)

**Use OpenAI API with gpt-4o-mini:**
```bash
python main.py
# Select: OpenAI API → Enter key → gpt-4o-mini
```
- ✅ Full tool support (file operations, code execution)
- ✅ Fast and reliable
- ✅ Cost-effective ($0.15 per 1M input tokens)

### 🆓 FREE Alternative (Full Features)

**Use OpenRouter free tier:**
```bash
# Get key: https://openrouter.ai/keys
python main.py
# Select: OpenAI API → OpenRouter → mistralai/devstral-2512:free
```
- ✅ Full tool support
- ✅ Completely FREE
- ⚠️ May have rate limits

### 💬 Chat-Only (LIMITED - Ollama)

**Use any Ollama model:**
```bash
ollama pull llama3.2:3b
python main.py
# Select: Ollama → any model
```
- ✅ Runs locally, private
- ✅ No API costs
- ❌ Chat only - NO file operations
- ❌ Cannot execute code or commands

---

**Bottom Line:** For actual coding work, use OpenAI API or OpenRouter. Ollama currently only works for chat/advice.
