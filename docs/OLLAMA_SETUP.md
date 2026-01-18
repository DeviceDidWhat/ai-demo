# Ollama Setup Guide

This guide helps you set up and use local AI models with Ollama.

## Installation

### Step 1: Install Ollama

Download and install from [ollama.ai](https://ollama.ai):

**Windows/Mac/Linux:**
```bash
# Visit https://ollama.ai/download
# Download and run the installer
```

**Verify Installation:**
```bash
ollama --version
```

### Step 2: Start Ollama

Ollama needs to be running to serve models:

**Option A: Desktop App**
- Start the Ollama desktop application
- It will run in the background

**Option B: Command Line**
```bash
ollama serve
```

### Step 3: Pull a Model

Download a model that **supports tool calling** (recommended for this AI agent):

```bash
# Recommended: Llama 3.2 (supports tools)
ollama pull llama3.2

# Alternative: Mistral (supports tools)
ollama pull mistral

# Alternative: Qwen 2.5 (supports tools)
ollama pull qwen2.5:7b
```

### Step 4: Verify Model

```bash
ollama list
```

You should see your downloaded model(s).

## Model Compatibility

### ✅ Models WITH Tool Support (Recommended)

These models work fully with the AI agent's file operations and code execution:

| Model | Size | Command | Notes |
|-------|------|---------|-------|
| Llama 3.2 | 2GB | `ollama pull llama3.2` | Fast, good for coding |
| Llama 3.1 | 4.7GB | `ollama pull llama3.1:8b` | Better quality |
| Mistral | 4.1GB | `ollama pull mistral` | Good general purpose |
| Mixtral | 26GB | `ollama pull mixtral` | High quality (needs GPU) |
| Qwen 2.5 | 4.7GB | `ollama pull qwen2.5:7b` | Good for code |

### ❌ Models WITHOUT Tool Support (Limited Mode)

These models run in basic chat mode only (no file/code operations):

| Model | Size | Command | Limitation |
|-------|------|---------|------------|
| DeepSeek Coder | 9GB | `ollama pull deepseek-coder-v2:16b` | No tool support |
| CodeLlama | 3.8GB | `ollama pull codellama` | No tool support |
| Llama 2 | 3.8GB | `ollama pull llama2` | No tool support |
| Phi | 1.6GB | `ollama pull phi` | No tool support |

## Using with AI Agent

### Start the Agent

```bash
python main.py
```

### Select Ollama

```
AI Agent - Model Provider Selection

Option  Provider         Description
1       OpenAI API       Use OpenAI models via API (requires API key and internet)
2       Ollama (Local)   Use local models with Ollama (requires Ollama installed)

Select provider: 2
```

### Choose Your Model

The agent will display all available models with tool support status:

```
Available Ollama Models:

#  Model Name              Size       Tools    Modified
1  llama3.2:latest        2.03 GB    Yes      2024-01-15
2  mistral:latest         4.11 GB    Yes      2024-01-14
3  deepseek-coder:16b     9.45 GB    No       2024-01-13

Select model: 1
```

### Tool Support Warning

If you select a model without tool support, you'll see:

```
⚠ Warning: This model does not support tool calling
  The agent will run in basic chat mode without file/code operations

⚠ Note: Running in basic chat mode
This model does not support tool calling.
File operations and code execution will not be available.
```

## Troubleshooting

### Error: "Ollama is not running!"

**Solution:**
```bash
# Start Ollama
ollama serve

# Or start the desktop application
```

### Error: "No Ollama models found!"

**Solution:**
```bash
# Pull a model first
ollama pull llama3.2

# Verify
ollama list
```

### Error: "does not support tools"

This happens when you select a model without tool support (like deepseek-coder).

**Solution:**
- Pull a model with tool support: `ollama pull llama3.2`
- Or continue in basic chat mode (no file operations)

### Slow Performance

**Solutions:**
1. Use a smaller model: `ollama pull llama3.2` (2GB)
2. Enable GPU acceleration (requires NVIDIA GPU):
   ```bash
   # Check if GPU is detected
   ollama run llama3.2
   ```
3. Close other applications to free RAM

### Out of Memory

**Solutions:**
1. Use a smaller model
2. Close other applications
3. Increase system RAM/swap

## Model Recommendations

### For Development/Testing
- **llama3.2** (2GB) - Fast, good enough for most tasks
- **qwen2.5:7b** (4.7GB) - Better code understanding

### For Production/Quality
- **llama3.1:8b** (4.7GB) - Better reasoning
- **mixtral** (26GB) - Highest quality (needs powerful hardware)

### Hardware Requirements

| Model Size | RAM Required | GPU (Optional) |
|------------|--------------|----------------|
| 2GB model  | 8GB RAM      | Any / None     |
| 4-5GB model| 16GB RAM     | 4GB+ VRAM      |
| 8GB+ model | 32GB RAM     | 8GB+ VRAM      |

## Advanced Configuration

### Custom Ollama Port

If Ollama runs on a different port:

```bash
# Set before starting agent
export BASE_URL="http://localhost:YOUR_PORT/v1"
python main.py --skip-model-selection
```

### Model Parameters

You can customize model parameters in `.ai-agent/config.toml`:

```toml
[model]
name = "llama3.2:latest"
temperature = 0.7
context_window = 128000
```

### Running Multiple Models

```bash
# Pull multiple models
ollama pull llama3.2
ollama pull mistral
ollama pull qwen2.5

# Switch between them in the agent
/model llama3.2:latest
/model mistral:latest
```

## Benefits of Ollama

✅ **Privacy** - All data stays on your machine
✅ **No API costs** - Free to use
✅ **Offline** - Works without internet
✅ **Fast** - No network latency
✅ **Control** - Choose any model

## Limitations

❌ **Hardware dependent** - Needs good CPU/RAM
❌ **Model quality** - May be lower than GPT-4
❌ **Some models lack tools** - Check compatibility first

## Next Steps

1. Install Ollama: https://ollama.ai
2. Pull a tool-compatible model: `ollama pull llama3.2`
3. Start the agent: `python main.py`
4. Select Ollama and enjoy!

For more information, see [MODEL_SELECTION.md](MODEL_SELECTION.md)
