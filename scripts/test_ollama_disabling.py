#!/usr/bin/env python3
"""Test Ollama tool disabling implementation"""

import sys
sys.path.insert(0, '.')

from config.config import Config, Provider
from client.llm_client import LLMClient
from prompts.system import get_system_prompt
from tools.registry import create_default_registry

print('='*60)
print('Testing Complete Flow: API vs Ollama Providers')
print('='*60)

# API Provider Test
print('\n[API Provider]')
print('-' * 40)
config_api = Config(provider=Provider.API)
client_api = LLMClient(config_api)
tools_api = create_default_registry(config_api).get_tools()
prompt_api = get_system_prompt(config_api, tools=tools_api)

print('✓ tools_supported:', client_api.tools_supported)
print('✓ Available tools:', len(tools_api))
print('✓ Has tool guidelines:', 'Tool Usage Guidelines' in prompt_api)
print('✓ Has Ollama limitations:', 'Ollama Model Limitations' in prompt_api)

assert client_api.tools_supported == True, "API should support tools"
assert 'Tool Usage Guidelines' in prompt_api, "API should have tool guidelines"
assert 'Ollama Model Limitations' not in prompt_api, "API should NOT have Ollama limitations"

# Ollama Provider Test
print('\n[Ollama Provider]')
print('-' * 40)
config_ollama = Config(provider=Provider.OLLAMA)
client_ollama = LLMClient(config_ollama)
tools_ollama = create_default_registry(config_ollama).get_tools()
prompt_ollama = get_system_prompt(config_ollama, tools=tools_ollama)

print('✓ tools_supported:', client_ollama.tools_supported)
print('✓ Available tools in registry:', len(tools_ollama))
print('✓ Has Ollama limitations:', 'Ollama Model Limitations' in prompt_ollama)
print('✓ Has chat-only warning:', 'chat-only' in prompt_ollama.lower())
print('✓ Has fallback message:', 'unable to perform' in prompt_ollama.lower())

assert client_ollama.tools_supported == False, "Ollama should NOT support tools"
assert 'Ollama Model Limitations' in prompt_ollama, "Ollama should have limitations notice"
assert 'chat-only' in prompt_ollama.lower(), "Ollama should mention chat-only"
assert 'unable to perform' in prompt_ollama.lower(), "Ollama should have fallback message"

print('\n' + '='*60)
print('✓ All flow tests passed successfully!')
print('✓ Ollama tool disabling is working as intended!')
print('='*60)
