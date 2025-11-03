"""Metasploit RPC client for executing auxiliary modules."""

from __future__ import annotations

import time
from typing import Any

from pymetasploit3.msfrpc import MsfRpcClient
from rich.console import Console

from .config import MsfConfig

console = Console()


class MsfAuxiliaryRunner:
    """Runner for Metasploit auxiliary modules."""
    
    def __init__(self, config: MsfConfig):
        """Initialize the MSF client.
        
        Args:
            config: Metasploit RPC configuration
        """
        self.config = config
        self.client: MsfRpcClient | None = None
    
    def connect(self) -> None:
        """Connect to Metasploit RPC server.
        
        Raises:
            ConnectionError: If connection fails
        """
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
                console.print("[green]✓[/green] Disconnected from Metasploit")
            except Exception:
                pass
            self.client = None
    
    def run_module(
        self, 
        module_path: str, 
        target: str, 
        options: dict[str, Any] | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Run an auxiliary module against a target.
        
        Args:
            module_path: Path to auxiliary module (e.g., 'auxiliary/scanner/portscan/tcp')
            target: Target host/IP
            options: Additional module options
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary containing module results
            
        Raises:
            ValueError: If module doesn't exist
            RuntimeError: If module execution fails
        """
        if not self.client:
            raise RuntimeError("Not connected to Metasploit. Call connect() first.")
        
        # Remove 'auxiliary/' prefix if present for module lookup
        module_name = module_path.replace("auxiliary/", "")
        
        try:
            # Get the module
            module = self.client.modules.use("auxiliary", module_name)
        except Exception as e:
            raise ValueError(f"Module '{module_path}' not found: {e}")
        
        # Set target
        module["RHOSTS"] = target
        
        # Set additional options
        if options:
            for key, value in options.items():
                module[key] = value
        
        console.print(f"[blue]►[/blue] Running {module_path} against {target}")
        
        # Execute module
        try:
            result = module.execute()
            
            # Wait for completion with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if module completed
                time.sleep(1)
                
                # For auxiliary modules, we check if job is done
                # This is a simplified approach - actual implementation may vary
                if hasattr(result, 'get') and result.get('job_id'):
                    job_id = result['job_id']
                    jobs = self.client.jobs.list
                    if str(job_id) not in jobs:
                        break
                else:
                    # If no job_id, module likely completed immediately
                    break
            
            return {
                "module": module_path,
                "target": target,
                "status": "completed",
                "result": result,
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute module: {e}")
    
    def get_module_info(self, module_path: str) -> dict[str, Any]:
        """Get information about a module.
        
        Args:
            module_path: Path to auxiliary module
            
        Returns:
            Dictionary containing module information
        """
        if not self.client:
            raise RuntimeError("Not connected to Metasploit. Call connect() first.")
        
        module_name = module_path.replace("auxiliary/", "")
        
        try:
            module = self.client.modules.use("auxiliary", module_name)
            return {
                "name": module.modulename,
                "description": module.description,
                "options": module.options,
                "required": module.required,
            }
        except Exception as e:
            raise ValueError(f"Module '{module_path}' not found: {e}")
