# Model Provider Selection Guide

This guide explains how to use the interactive model selection feature when starting the AI coding agent.

## Overview

When you start the AI agent, you can now choose between two model providers:

1. **OpenAI API** - Use cloud-based models from OpenAI or compatible providers
2. **Ollama** - Use local models running on your machine

## Quick Start

### Option 1: Interactive Selection (Default)

Simply run the agent without any environment variables set:

```bash
python main.py
```

You'll be prompted to:
1. Select a provider (OpenAI API or Ollama)
2. Configure the selected provider
3. Choose a model

### Option 2: Skip Selection (Use Environment Variables)

If you already have `API_KEY` set in your environment, or want to skip the interactive selection:

```bash
python main.py --skip-model-selection
```

Or set environment variables before running:

```bash
export API_KEY="your-api-key"
export BASE_URL="https://api.openai.com/v1"  # Optional
python main.py
```

## Provider Configuration

### OpenAI API Configuration

When you select OpenAI API, you'll be prompted for:

1. **API Key**: Your OpenAI API key or compatible provider key
2. **API Provider**: Choose from:
   - OpenAI (https://api.openai.com/v1)
   - OpenRouter (https://openrouter.ai/api/v1)
   - Custom URL
3. **Model Name**: The model to use (e.g., `gpt-4o`, `gpt-3.5-turbo`)

#### Example: Using OpenAI

```
Select provider: 1 (OpenAI API)
Enter your API key: sk-...
Select API provider: 1 (OpenAI)
Enter model name: gpt-4o
```

#### Example: Using OpenRouter

```
Select provider: 1 (OpenAI API)
Enter your API key: sk-or-v1-...
Select API provider: 2 (OpenRouter)
Enter model name: mistralai/devstral-2512:free
```

### Ollama Configuration

When you select Ollama, the agent will:

1. **Check if Ollama is running** on `http://localhost:11434`
2. **List available models** installed locally
3. **Let you select** from the available models

#### Prerequisites for Ollama

Before selecting Ollama, ensure:

1. Ollama is installed: https://ollama.ai
2. Ollama service is running:
   ```bash
   ollama serve
   ```
   Or start the Ollama desktop application

3. At least one model is pulled:
   ```bash
   ollama pull llama3.2
   # or
   ollama pull mistral
   # or
   ollama pull codellama
   ```

#### Example: Using Ollama

```
Select provider: 2 (Ollama)

Available Ollama Models:
#  Model Name              Size       Modified
1  llama3.2:latest        2.03 GB    2024-01-15
2  mistral:latest         4.11 GB    2024-01-14
3  codellama:latest       3.83 GB    2024-01-13

Select model: 1
```

## Environment Variables

The model selection sets these environment variables:

- `API_KEY`: Your API key (required)
- `BASE_URL`: The base URL for the API (optional, defaults to OpenAI)

### For OpenAI/OpenRouter

```bash
export API_KEY="sk-..."
export BASE_URL="https://api.openai.com/v1"
```

### For Ollama

```bash
export API_KEY="ollama"  # Placeholder, Ollama doesn't validate
export BASE_URL="http://localhost:11434/v1"
```

## Troubleshooting

### Ollama Issues

**Error: "Ollama is not running!"**

Solution:
```bash
# Start Ollama service
ollama serve

# Or start the desktop application
```

**Error: "No Ollama models found!"**

Solution:
```bash
# Pull a model first
ollama pull llama3.2

# List available models to verify
ollama list
```

**Error: "Could not fetch Ollama models"**

Solution:
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Verify Ollama is installed: `ollama --version`
- Check firewall/network settings

### OpenAI API Issues

**Error: "No API key found"**

Solution:
- Run without `--skip-model-selection` flag
- Or set `API_KEY` environment variable

**Error: "Connection error"**

Solution:
- Check your internet connection
- Verify the BASE_URL is correct
- For custom APIs, ensure they're OpenAI-compatible

## Command Line Options

```bash
python main.py [OPTIONS] [PROMPT]

Options:
  --cwd, -c PATH              Current working directory
  --skip-model-selection      Skip interactive model selection
  --help                      Show help message
```

## Advanced Usage

### Using Different Models

You can change models during an interactive session:

```bash
/model gpt-4o-mini
```

### Configuration File

The agent also supports configuration via `.ai-agent/config.toml`:

```toml
[model]
name = "gpt-4o"
temperature = 0.7
context_window = 128000
```

However, the interactive model selection will override these settings if no `API_KEY` is found.

## Supported Models

### OpenAI Models
- GPT-4o
- GPT-4o-mini
- GPT-4-turbo
- GPT-3.5-turbo

### OpenRouter Models
- Mistral models (devstral, mixtral)
- Claude models
- Llama models
- And many more: https://openrouter.ai/models

### Ollama Models
Any model available through Ollama:
- Llama 3.2, 3.1, 2
- Mistral
- CodeLlama
- Phi
- Gemma
- And more: https://ollama.ai/library

## Best Practices

1. **For Development**: Use Ollama with local models to avoid API costs
2. **For Production**: Use OpenAI API or OpenRouter for better performance
3. **For Privacy**: Use Ollama to keep all data local
4. **For Experimentation**: Use OpenRouter to try different models easily

## FAQ

**Q: Can I use both OpenAI and Ollama in the same session?**

A: No, you select one provider at startup. However, you can restart the agent to switch providers.

**Q: Does model selection work with MCP servers?**

A: Yes, model selection is independent of MCP server configuration.

**Q: Can I use custom OpenAI-compatible APIs?**

A: Yes, select "Custom URL" when configuring OpenAI API and enter your endpoint.

**Q: How do I reset my model selection?**

A: Simply restart the agent without setting environment variables, and you'll be prompted again.

**Q: Can I bypass the selection for scripting?**

A: Yes, use `--skip-model-selection` and set `API_KEY` and `BASE_URL` environment variables.
