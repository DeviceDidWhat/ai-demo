"""
Model Provider Selection Module

This module provides interactive selection of model providers (OpenAI API or Ollama local)
at application startup.
"""

import os
from enum import Enum
from typing import Optional
import httpx
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table


class ModelProvider(str, Enum):
    """Available model providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"


class ModelSelector:
    """Handles interactive model provider and model selection"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.ollama_base_url = "http://localhost:11434"

    def select_provider(self) -> ModelProvider:
        """
        Prompt user to select between OpenAI API and Ollama

        Returns:
            ModelProvider: Selected provider
        """
        self.console.print("\n[bold cyan]AI Agent - Model Provider Selection[/bold cyan]\n")

        # Create selection table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Provider", style="green", width=20)
        table.add_column("Description", style="white")

        table.add_row(
            "1",
            "OpenAI API",
            "Use OpenAI models via API (requires API key and internet)"
        )
        table.add_row(
            "2",
            "Ollama (Local)",
            "Use local models with Ollama (requires Ollama installed)"
        )

        self.console.print(table)
        self.console.print()

        # Get user choice
        choice = Prompt.ask(
            "[bold]Select provider[/bold]",
            choices=["1", "2"],
            default="1"
        )

        if choice == "1":
            return ModelProvider.OPENAI
        else:
            return ModelProvider.OLLAMA

    def check_ollama_running(self) -> bool:
        """
        Check if Ollama service is running locally

        Returns:
            bool: True if Ollama is running, False otherwise
        """
        try:
            response = httpx.get(f"{self.ollama_base_url}/api/tags", timeout=3.0)
            return response.status_code == 200
        except Exception:
            return False

    def get_ollama_models(self) -> list[dict]:
        """
        Fetch available Ollama models from local instance

        Returns:
            list[dict]: List of available models with their metadata
        """
        try:
            response = httpx.get(f"{self.ollama_base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])

                # Check tool support for each model
                for model in models:
                    model["supports_tools"] = self._check_tool_support(model.get("name", ""))

                return models
            return []
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not fetch Ollama models: {e}[/yellow]")
            return []

    def _check_tool_support(self, model_name: str) -> bool:  # noqa: ARG002
        """
        Check if a model supports tool/function calling

        IMPORTANT: As of Ollama v0.14.2, the OpenAI-compatible tool calling API has bugs
        that cause "invalid tool call arguments" errors even with models that should support tools.

        Until Ollama fixes this issue, ALL Ollama models are marked as not supporting tools.
        This means they run in basic chat mode only.

        For full tool support (file operations, code execution, etc.), users should use:
        - OpenAI API (gpt-4o, gpt-4o-mini, etc.)
        - OpenRouter with compatible models
        - Other OpenAI-compatible API providers

        Args:
            model_name: Name of the model

        Returns:
            bool: Always False for Ollama models until tool calling is fixed
        """
        # Always return False for Ollama models due to current tool calling bugs
        return False

    def select_ollama_model(self) -> Optional[str]:
        """
        Interactive selection of Ollama model

        Returns:
            Optional[str]: Selected model name or None if no models available
        """
        if not self.check_ollama_running():
            self.console.print("\n[bold red]Error: Ollama is not running![/bold red]")
            self.console.print("[yellow]Please start Ollama first:[/yellow]")
            self.console.print("  - Run: [cyan]ollama serve[/cyan]")
            self.console.print("  - Or start Ollama desktop application\n")
            return None

        models = self.get_ollama_models()

        if not models:
            self.console.print("\n[bold red]No Ollama models found![/bold red]")
            self.console.print("[yellow]Please pull a model first:[/yellow]")
            self.console.print("  - Run: [cyan]ollama pull llama3.2[/cyan]")
            self.console.print("  - Or: [cyan]ollama pull mistral[/cyan]\n")
            return None

        # Display available models
        self.console.print("\n[bold cyan]Available Ollama Models:[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=5)
        table.add_column("Model Name", style="green", width=35)
        table.add_column("Size", style="yellow", width=12)
        table.add_column("Tools", style="white", width=8)
        table.add_column("Modified", style="dim", width=12)

        for idx, model in enumerate(models, 1):
            name = model.get("name", "unknown")
            size_bytes = model.get("size", 0)
            size_gb = size_bytes / (1024**3) if size_bytes else 0
            modified = model.get("modified_at", "unknown")[:10]
            supports_tools = model.get("supports_tools", False)

            tool_status = "[green]Yes[/green]" if supports_tools else "[red]No[/red]"

            table.add_row(
                str(idx),
                name,
                f"{size_gb:.2f} GB",
                tool_status,
                modified
            )

        self.console.print(table)
        self.console.print("\n[bold red]⚠ OLLAMA LIMITATION:[/bold red]")
        self.console.print("[yellow]  • Ollama v0.14.2 has bugs with OpenAI-compatible tool calling[/yellow]")
        self.console.print("[yellow]  • ALL Ollama models run in basic chat mode (NO file operations)[/yellow]")
        self.console.print("[yellow]  • For full coding features, use OpenAI API instead[/yellow]")
        self.console.print()

        # Get user choice
        choices = [str(i) for i in range(1, len(models) + 1)]
        choice = Prompt.ask(
            "[bold]Select model[/bold]",
            choices=choices,
            default="1"
        )

        selected_model = models[int(choice) - 1]
        return selected_model.get("name")

    def configure_openai(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Configure OpenAI API settings

        Returns:
            tuple: (api_key, base_url, model_name)
        """
        self.console.print("\n[bold cyan]OpenAI Configuration[/bold cyan]\n")

        # Check for existing API key
        existing_api_key = os.environ.get("API_KEY")

        if existing_api_key:
            self.console.print(f"[green]Found existing API_KEY in environment[/green]")
            use_existing = Confirm.ask("Use existing API key?", default=True)
            if use_existing:
                api_key = existing_api_key
            else:
                self.console.print("\n[dim]Tip: You can paste by right-clicking or Ctrl+V[/dim]")
                api_key = Prompt.ask("[bold]Enter your API key[/bold]", password=False)
        else:
            self.console.print("\n[dim]Tip: You can paste by right-clicking or Ctrl+V[/dim]")
            self.console.print("[dim]Your input will be visible on screen[/dim]")
            api_key = Prompt.ask("[bold]Enter your API key[/bold]", password=False)

        # Base URL configuration
        self.console.print("\n[bold]API Provider:[/bold]")
        self.console.print("  1. OpenAI (https://api.openai.com/v1)")
        self.console.print("  2. OpenRouter (https://openrouter.ai/api/v1)")
        self.console.print("  3. Custom URL\n")

        provider_choice = Prompt.ask(
            "Select API provider",
            choices=["1", "2", "3"],
            default="1"
        )

        if provider_choice == "1":
            base_url = "https://api.openai.com/v1"
            default_model = "gpt-4o"
        elif provider_choice == "2":
            base_url = "https://openrouter.ai/api/v1"
            default_model = "mistralai/devstral-2512:free"
        else:
            base_url = Prompt.ask("[bold]Enter custom base URL[/bold]")
            default_model = "gpt-4o"

        # Model name
        model_name = Prompt.ask(
            "[bold]Enter model name[/bold]",
            default=default_model
        )

        return api_key, base_url, model_name

    def configure_ollama(self) -> tuple[Optional[str], str, Optional[str], bool]:
        """
        Configure Ollama settings

        Returns:
            tuple: (api_key, base_url, model_name, supports_tools)
        """
        models = self.get_ollama_models()

        if not models:
            if not self.check_ollama_running():
                self.console.print("\n[bold red]Error: Ollama is not running![/bold red]")
                self.console.print("[yellow]Please start Ollama first:[/yellow]")
                self.console.print("  - Run: [cyan]ollama serve[/cyan]")
                self.console.print("  - Or start Ollama desktop application\n")
            else:
                self.console.print("\n[bold red]No Ollama models found![/bold red]")
                self.console.print("[yellow]Please pull a model first:[/yellow]")
                self.console.print("  - Run: [cyan]ollama pull llama3.2[/cyan]")
                self.console.print("  - Or: [cyan]ollama pull mistral[/cyan]\n")
            return None, None, None, False

        model_name = self.select_ollama_model()

        if not model_name:
            return None, None, None, False

        # Find the selected model to check tool support
        selected_model = next((m for m in models if m.get("name") == model_name), None)
        supports_tools = selected_model.get("supports_tools", False) if selected_model else False

        # Ollama doesn't require or validate API keys
        api_key = None
        base_url = f"{self.ollama_base_url}/v1"

        self.console.print(f"\n[green]✓ Configured Ollama with model: {model_name}[/green]")
        self.console.print(f"[dim]Base URL: {base_url}[/dim]")

        # Ollama models don't support tools due to current bugs
        self.console.print(f"\n[bold yellow]⚠ OLLAMA LIMITATION[/bold yellow]")
        self.console.print(f"[yellow]Due to bugs in Ollama v0.14.2, tool calling is disabled.[/yellow]")
        self.console.print(f"[yellow]This model will run in CHAT-ONLY mode:[/yellow]")
        self.console.print(f"  ✗ No file operations (read, write, edit)")
        self.console.print(f"  ✗ No shell command execution")
        self.console.print(f"  ✗ No code manipulation")
        self.console.print(f"  ✓ Can provide advice, explanations, and code suggestions")
        self.console.print(f"\n[cyan]For full coding features, use OpenAI API instead:[/cyan]")
        self.console.print(f"  • GPT-4o: Full tool support, best quality")
        self.console.print(f"  • GPT-4o-mini: Full tool support, cost-effective")
        self.console.print(f"  • OpenRouter: Various models with tool support")

        proceed = Confirm.ask(f"\n[bold]Continue with {model_name} in chat-only mode?[/bold]", default=True)
        if not proceed:
            return None, None, None, False

        self.console.print()

        return api_key, base_url, model_name, supports_tools

    def run_selection(self) -> Optional[dict]:
        """
        Run the complete model selection flow

        Returns:
            dict: Configuration dictionary with api_key, base_url, model_name, and supports_tools
            None: If configuration failed
        """
        provider = self.select_provider()

        supports_tools = True  # OpenAI always supports tools

        if provider == ModelProvider.OPENAI:
            api_key, base_url, model_name = self.configure_openai()
        else:
            api_key, base_url, model_name, supports_tools = self.configure_ollama()

            if not model_name:
                # Ollama configuration failed
                self.console.print("[bold red]Failed to configure Ollama. Exiting.[/bold red]")
                return None

        return {
            "provider": provider.value,
            "api_key": api_key,
            "base_url": base_url,
            "model_name": model_name,
            "supports_tools": supports_tools,
        }
