from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .ai_analyzer import AIAnalyzer
from .ai_module_selector import AIModuleSelector
from .config import load_config
from .msf_client import MsfAuxiliaryRunner
from .msf_runner import UniversalMsfRunner
from .reporter import ScanReporter

app = typer.Typer(add_completion=False, help="Non-operational scaffold for authorized auditing workflows.")
console = Console()


@app.command()
def version() -> None:
    """Show version."""
    console.print(__version__)


@app.command()
def info() -> None:
    """Show important usage information."""
    msg = (
        "This CLI is a scaffold and does not execute Metasploit or any network actions.\n"
        "Use only for planning and reporting within an authorized assessment scope."
    )
    console.print(Panel(msg, title="Info", style="yellow"))


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target host/IP"),
    config: Path = typer.Option("aux_modules.json", "--config", "-c", help="Configuration file path"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output report file (json/yaml/txt)"),
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Specific module to run (overrides config)"),
) -> None:
    """Run auxiliary scans against target.
    
    Requires Metasploit RPC to be running:
    msfrpcd -P <password> -U msf -a 127.0.0.1
    """
    try:
        # Load configuration
        if not config.exists():
            console.print(f"[red]✗[/red] Configuration file not found: {config}")
            console.print("\nCreate a config file based on aux_modules.sample.json")
            raise typer.Exit(code=1)
        
        cfg = load_config(config)
        
        # Determine which modules to run
        modules_to_run = [module] if module else cfg.allowed_modules
        
        if not modules_to_run:
            console.print("[yellow]![/yellow] No modules specified. Add modules to config or use --module")
            raise typer.Exit(code=1)
        
        # Validate modules are allowed (if using config)
        if module and module not in cfg.allowed_modules:
            console.print(f"[yellow]⚠[/yellow] Module '{module}' not in allowed list, but proceeding...")
        
        # Initialize reporter
        reporter = ScanReporter()
        
        # Initialize MSF client
        runner = MsfAuxiliaryRunner(cfg.msf_config)
        
        try:
            # Connect to Metasploit
            runner.connect()
            
            # Run each module
            for mod in modules_to_run:
                try:
                    console.print(f"\n[bold]Running module:[/bold] {mod}")
                    result = runner.run_module(mod, target, timeout=cfg.timeout)
                    reporter.add_result(result)
                    console.print(f"[green]✓[/green] Module completed: {mod}")
                except Exception as e:
                    console.print(f"[red]✗[/red] Module failed: {mod} - {e}")
                    reporter.add_result({
                        "module": mod,
                        "target": target,
                        "status": "failed",
                        "error": str(e),
                    })
            
        finally:
            # Disconnect from Metasploit
            runner.disconnect()
        
        # Display results
        console.print("\n")
        reporter.print_summary()
        
        # Save report if requested
        if output:
            ext = output.suffix.lower()
            if ext == ".json":
                reporter.save_json(output)
            elif ext in [".yaml", ".yml"]:
                reporter.save_yaml(output)
            else:
                reporter.save_text(output)
        
        console.print("\n[green]✓[/green] Scan completed")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]![/yellow] Scan interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def ai_scan(
    target: str = typer.Argument(..., help="Target (URL, IP, hostname)"),
    config: Path = typer.Option("aux_modules.json", "--config", "-c", help="Configuration file path"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output report file"),
    priority: str = typer.Option("high", "--priority", "-p", help="Minimum priority (high/medium/low)"),
    auto_run: bool = typer.Option(False, "--auto-run", "-a", help="Automatically run selected modules"),
) -> None:
    """AI-powered module selection and scanning.
    
    The AI analyzes the target and automatically selects appropriate
    Metasploit modules (auxiliaries, exploits, payloads, etc.) to run.
    """
    try:
        # Load configuration
        if not config.exists():
            console.print(f"[red]✗[/red] Configuration file not found: {config}")
            raise typer.Exit(code=1)
        
        cfg = load_config(config)
        
        # Check if AI is configured
        if not cfg.ai_config.enabled and not cfg.ai_config.api_key:
            console.print("[yellow]⚠[/yellow] AI not configured. Set ai_config in your config file or use environment variables.")
            console.print("\nRequired: OPENAI_API_KEY or ANTHROPIC_API_KEY")
            raise typer.Exit(code=1)
        
        # Initialize AI module selector
        selector = AIModuleSelector(
            provider=cfg.ai_config.provider,
            api_key=cfg.ai_config.api_key if cfg.ai_config.api_key else None,
            model=cfg.ai_config.model if cfg.ai_config.model else None,
        )
        
        # Select modules using AI
        selection = selector.select_modules(target, verbose=True)
        
        if "error" in selection:
            console.print(f"[red]✗[/red] Module selection failed")
            raise typer.Exit(code=1)
        
        # Filter by priority
        if priority in ["high", "medium", "low"]:
            selection = selector.filter_by_priority(selection, priority)  # type: ignore
        
        # Build module list for execution
        all_modules = []
        if "modules" in selection:
            for module_type in ["auxiliary", "exploit", "payload", "encoder", "nop", "post", "evasion"]:
                for mod in selection["modules"].get(module_type, []):
                    all_modules.append({
                        "module_type": module_type,
                        "module": mod.get("module"),
                        "options": mod.get("options", {}),
                        "priority": mod.get("priority", "low"),
                    })
        
        if not all_modules:
            console.print("[yellow]![/yellow] No modules selected")
            raise typer.Exit(code=0)
        
        # Ask user if they want to run the modules
        if not auto_run:
            console.print(f"\n[bold]Run {len(all_modules)} selected modules against {target}?[/bold]")
            response = typer.confirm("Continue")
            if not response:
                console.print("[yellow]Scan cancelled[/yellow]")
                raise typer.Exit(code=0)
        
        # Initialize MSF runner and reporter
        runner = UniversalMsfRunner(cfg.msf_config, verbose=True)
        reporter = ScanReporter()
        
        try:
            # Connect to Metasploit
            runner.connect()
            
            # Run modules
            results = runner.run_module_sequence(
                modules=all_modules,
                target=target,
                timeout=cfg.timeout,
            )
            
            # Add results to reporter
            for result in results:
                reporter.add_result(result)
            
        finally:
            runner.disconnect()
        
        # Run AI analysis on results if configured
        if cfg.ai_config.enabled:
            console.print("\n[bold blue]Running AI analysis on results...[/bold blue]")
            analyzer = AIAnalyzer(
                provider=cfg.ai_config.provider,
                api_key=cfg.ai_config.api_key if cfg.ai_config.api_key else None,
            )
            analysis = analyzer.analyze_results(reporter.results)
            reporter.ai_analysis = analysis  # type: ignore
        
        # Display results
        console.print("\n")
        reporter.print_summary()
        
        # Save report if requested
        if output:
            ext = output.suffix.lower()
            if ext == ".json":
                reporter.save_json(output)
            elif ext in [".yaml", ".yml"]:
                reporter.save_yaml(output)
            else:
                reporter.save_text(output)
        
        console.print("\n[green]✓[/green] AI-powered scan completed")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]![/yellow] Scan interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]✗[/red] Error: {e}")
        raise typer.Exit(code=1)


def main(argv: Optional[list[str]] = None) -> int:
    try:
        app()
        return 0
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0


if __name__ == "__main__":
    sys.exit(main())
