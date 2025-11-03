"""Report generation for scan results."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

console = Console()


class ScanReporter:
    """Generate reports from scan results."""
    
    def __init__(self):
        """Initialize the reporter."""
        self.results: list[dict[str, Any]] = []
    
    def add_result(self, result: dict[str, Any]) -> None:
        """Add a scan result.
        
        Args:
            result: Scan result dictionary
        """
        self.results.append({
            **result,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def print_summary(self) -> None:
        """Print a summary table of results to console."""
        if not self.results:
            console.print("[yellow]No results to display[/yellow]")
            return
        
        table = Table(title="Scan Results Summary")
        table.add_column("Module", style="cyan")
        table.add_column("Target", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Timestamp", style="blue")
        
        for result in self.results:
            table.add_row(
                result.get("module", "unknown"),
                result.get("target", "unknown"),
                result.get("status", "unknown"),
                result.get("timestamp", "unknown"),
            )
        
        console.print(table)
    
    def save_json(self, output_path: Path | str) -> None:
        """Save results to JSON file.
        
        Args:
            output_path: Path to output file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"[green]✓[/green] Results saved to {path}")
    
    def save_yaml(self, output_path: Path | str) -> None:
        """Save results to YAML file.
        
        Args:
            output_path: Path to output file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            yaml.dump(self.results, f, default_flow_style=False)
        
        console.print(f"[green]✓[/green] Results saved to {path}")
    
    def save_text(self, output_path: Path | str) -> None:
        """Save results to text file.
        
        Args:
            output_path: Path to output file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("MSF AUXILIARY SCAN REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            for i, result in enumerate(self.results, 1):
                f.write(f"Result {i}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Module: {result.get('module', 'unknown')}\n")
                f.write(f"Target: {result.get('target', 'unknown')}\n")
                f.write(f"Status: {result.get('status', 'unknown')}\n")
                f.write(f"Timestamp: {result.get('timestamp', 'unknown')}\n")
                f.write(f"\nDetails:\n{json.dumps(result.get('result', {}), indent=2)}\n")
                f.write("\n" + "=" * 80 + "\n\n")
        
        console.print(f"[green]✓[/green] Results saved to {path}")
