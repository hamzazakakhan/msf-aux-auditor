"""Universal Metasploit module runner for all module types."""

from __future__ import annotations

import time
from typing import Any, Literal

from pymetasploit3.msfrpc import MsfRpcClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import MsfConfig

console = Console()

ModuleType = Literal["auxiliary", "exploit", "payload", "encoder", "nop", "post", "evasion"]


class UniversalMsfRunner:
    """Universal runner for all Metasploit module types."""
    
    def __init__(self, config: MsfConfig, verbose: bool = True):
        """Initialize the MSF runner.
        
        Args:
            config: Metasploit RPC configuration
            verbose: Enable verbose output
        """
        self.config = config
        self.verbose = verbose
        self.client: MsfRpcClient | None = None
    
    def connect(self) -> None:
        """Connect to Metasploit RPC server."""
        if self.verbose:
            console.print(f"\n[yellow]→[/yellow] Connecting to Metasploit RPC...")
            console.print(f"  • Host: {self.config.host}")
            console.print(f"  • Port: {self.config.port}")
            console.print(f"  • User: {self.config.username}")
        
        try:
            self.client = MsfRpcClient(
                password=self.config.password,
                username=self.config.username,
                server=self.config.host,
                port=self.config.port,
                ssl=self.config.ssl,
            )
            console.print(f"[green]✓[/green] Connected to Metasploit at {self.config.host}:{self.config.port}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Metasploit RPC: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from Metasploit RPC server."""
        if self.client:
            try:
                self.client.logout()
                if self.verbose:
                    console.print("[green]✓[/green] Disconnected from Metasploit")
            except Exception:
                pass
            self.client = None
    
    def run_module(
        self,
        module_type: ModuleType,
        module_path: str,
        target: str,
        options: dict[str, Any] | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Run any type of Metasploit module.
        
        Args:
            module_type: Type of module (auxiliary, exploit, etc.)
            module_path: Path to module
            target: Target host/IP
            options: Module options
            timeout: Execution timeout
            
        Returns:
            Dictionary containing module results
        """
        if not self.client:
            raise RuntimeError("Not connected to Metasploit. Call connect() first.")
        
        if self.verbose:
            console.print(f"\n{'='*80}")
            console.print(f"[bold cyan]EXECUTING MODULE[/bold cyan]")
            console.print(f"{'='*80}")
            console.print(f"[cyan]Type:[/cyan] {module_type}")
            console.print(f"[cyan]Module:[/cyan] {module_path}")
            console.print(f"[cyan]Target:[/cyan] {target}")
        
        # Extract module name without type prefix
        module_name = module_path
        for prefix in ["auxiliary/", "exploit/", "payload/", "encoder/", "nop/", "post/", "evasion/"]:
            module_name = module_name.replace(prefix, "")
        
        try:
            # Get the module
            if self.verbose:
                console.print(f"\n[yellow]→[/yellow] Loading module...")
            
            module = self.client.modules.use(module_type, module_name)
            
            if self.verbose:
                console.print(f"[green]✓[/green] Module loaded: {module.modulename}")
                if hasattr(module, 'description') and module.description:
                    console.print(f"[dim]Description: {module.description}[/dim]")
        
        except Exception as e:
            raise ValueError(f"Module '{module_path}' not found or invalid: {e}")
        
        # Set target based on module type
        if module_type in ["auxiliary", "exploit"]:
            module["RHOSTS"] = target
            if self.verbose:
                console.print(f"\n[yellow]→[/yellow] Setting target: RHOSTS={target}")
        
        # Set additional options
        if options:
            if self.verbose:
                console.print(f"\n[yellow]→[/yellow] Configuring module options:")
            
            for key, value in options.items():
                try:
                    module[key] = value
                    if self.verbose:
                        # Mask sensitive values
                        display_value = "***" if any(s in key.lower() for s in ["pass", "key", "secret", "token"]) else value
                        console.print(f"  • {key} = {display_value}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Failed to set {key}: {e}")
        
        # Display module info if verbose
        if self.verbose and hasattr(module, 'options'):
            console.print(f"\n[cyan]Available Options:[/cyan]")
            for opt_name, opt_info in module.options.items():
                required = "[red]*[/red]" if opt_info.get('required') else " "
                current = module.get(opt_name, opt_info.get('default', ''))
                console.print(f"  {required} {opt_name}: {current}")
                if opt_info.get('desc'):
                    console.print(f"     [dim]{opt_info['desc']}[/dim]")
        
        # Execute module
        console.print(f"\n[bold yellow]▶ EXECUTING MODULE...[/bold yellow]")
        
        try:
            start_time = time.time()
            result = module.execute()
            
            if self.verbose:
                console.print(f"[green]✓[/green] Module execution initiated")
            
            # Wait for completion with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Running module...", total=None)
                
                while time.time() - start_time < timeout:
                    time.sleep(1)
                    elapsed = int(time.time() - start_time)
                    progress.update(task, description=f"[cyan]Running module... ({elapsed}s)")
                    
                    # Check if job completed
                    if hasattr(result, 'get') and result.get('job_id'):
                        job_id = result['job_id']
                        jobs = self.client.jobs.list
                        if str(job_id) not in jobs:
                            if self.verbose:
                                console.print(f"[green]✓[/green] Job {job_id} completed")
                            break
                    else:
                        # No job_id, module completed immediately
                        break
            
            execution_time = time.time() - start_time
            
            if self.verbose:
                console.print(f"\n[green]✓[/green] Module completed in {execution_time:.2f}s")
                console.print(f"{'='*80}\n")
            
            return {
                "module": module_path,
                "module_type": module_type,
                "target": target,
                "status": "completed",
                "execution_time": execution_time,
                "result": result,
            }
            
        except Exception as e:
            console.print(f"\n[red]✗[/red] Module execution failed: {e}")
            raise RuntimeError(f"Failed to execute module: {e}")
    
    def run_module_sequence(
        self,
        modules: list[dict[str, Any]],
        target: str,
        timeout: int = 300,
    ) -> list[dict[str, Any]]:
        """Run a sequence of modules.
        
        Args:
            modules: List of module specifications
            target: Target host/IP
            timeout: Per-module timeout
            
        Returns:
            List of results
        """
        results = []
        
        console.print(f"\n[bold blue]STARTING MODULE SEQUENCE[/bold blue]")
        console.print(f"Target: {target}")
        console.print(f"Total modules: {len(modules)}\n")
        
        for i, mod_spec in enumerate(modules, 1):
            module_type = mod_spec.get("module_type", "auxiliary")
            module_path = mod_spec.get("module")
            options = mod_spec.get("options", {})
            
            console.print(f"\n[bold]Module {i}/{len(modules)}[/bold]")
            
            try:
                result = self.run_module(
                    module_type=module_type,
                    module_path=module_path,
                    target=target,
                    options=options,
                    timeout=timeout,
                )
                results.append(result)
                console.print(f"[green]✓[/green] Module {i} completed successfully")
                
            except Exception as e:
                error_result = {
                    "module": module_path,
                    "module_type": module_type,
                    "target": target,
                    "status": "failed",
                    "error": str(e),
                }
                results.append(error_result)
                console.print(f"[red]✗[/red] Module {i} failed: {e}")
                
                # Ask if user wants to continue
                if i < len(modules):
                    console.print("[yellow]Continue with remaining modules? (Ctrl+C to abort)[/yellow]")
                    time.sleep(2)
        
        console.print(f"\n[bold green]SEQUENCE COMPLETE[/bold green]")
        console.print(f"Successful: {sum(1 for r in results if r.get('status') == 'completed')}/{len(results)}")
        
        return results
    
    def get_module_info(self, module_type: ModuleType, module_path: str) -> dict[str, Any]:
        """Get detailed information about a module.
        
        Args:
            module_type: Type of module
            module_path: Path to module
            
        Returns:
            Module information dictionary
        """
        if not self.client:
            raise RuntimeError("Not connected to Metasploit. Call connect() first.")
        
        module_name = module_path
        for prefix in ["auxiliary/", "exploit/", "payload/", "encoder/", "nop/", "post/", "evasion/"]:
            module_name = module_name.replace(prefix, "")
        
        try:
            module = self.client.modules.use(module_type, module_name)
            return {
                "name": module.modulename,
                "type": module_type,
                "description": getattr(module, 'description', ''),
                "options": module.options if hasattr(module, 'options') else {},
                "required": module.required if hasattr(module, 'required') else [],
            }
        except Exception as e:
            raise ValueError(f"Module '{module_path}' not found: {e}")
