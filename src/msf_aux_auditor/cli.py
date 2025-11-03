from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .config import load_config
from .msf_client import MsfAuxiliaryRunner
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


def main(argv: Optional[list[str]] = None) -> int:
    try:
        app()
        return 0
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0


if __name__ == "__main__":
    sys.exit(main())
