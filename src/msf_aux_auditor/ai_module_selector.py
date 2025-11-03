"""AI-powered Metasploit module selection based on target analysis."""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

console = Console()

AIProvider = Literal["openai", "anthropic"]
ModuleType = Literal["auxiliary", "exploit", "payload", "encoder", "nop", "post", "evasion"]


class AIModuleSelector:
    """Use AI to intelligently select Metasploit modules based on target analysis."""
    
    def __init__(
        self, 
        provider: AIProvider = "openai",
        api_key: str | None = None,
        model: str | None = None,
    ):
        """Initialize the AI module selector.
        
        Args:
            provider: AI provider to use ('openai' or 'anthropic')
            api_key: API key for the provider (falls back to env vars)
            model: Model to use (defaults based on provider)
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        # Initialize client based on provider
        if provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model or "gpt-4o"
        elif provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def select_modules(self, target: str, target_info: dict[str, Any] | None = None, verbose: bool = True) -> dict[str, Any]:
        """Analyze target and select appropriate Metasploit modules.
        
        Args:
            target: Target URL, IP address, or hostname
            target_info: Optional additional information about the target
            verbose: Enable verbose output with detailed reasoning
            
        Returns:
            Dictionary containing selected modules organized by type with rationale
        """
        console.print("\n" + "="*80)
        console.print(f"[bold blue]🤖 AI-POWERED MODULE SELECTION[/bold blue]")
        console.print("="*80)
        console.print(f"\n[cyan]Target:[/cyan] {target}")
        
        if target_info and verbose:
            console.print(f"[cyan]Additional Info:[/cyan]")
            for key, value in target_info.items():
                console.print(f"  • {key}: {value}")
        
        console.print(f"\n[yellow]→[/yellow] Analyzing target characteristics...")
        console.print(f"[yellow]→[/yellow] Consulting AI ({self.provider}/{self.model})...")
        
        # Build the analysis prompt
        prompt = self._build_selection_prompt(target, target_info)
        
        if verbose:
            console.print(f"[dim]Prompt length: {len(prompt)} characters[/dim]")
        
        try:
            # Get module recommendations from AI
            if self.provider == "openai":
                response = self._select_with_openai(prompt)
            else:
                response = self._select_with_anthropic(prompt)
            
            # Parse the response
            modules = self._parse_selection(response)
            
            # Display verbose results
            if verbose and "target_analysis" in modules:
                console.print(f"\n[bold green]📊 TARGET ANALYSIS:[/bold green]")
                console.print(f"[dim]{modules['target_analysis']}[/dim]")
            
            if verbose and "execution_order" in modules:
                console.print(f"\n[bold yellow]📋 RECOMMENDED EXECUTION ORDER:[/bold yellow]")
                for i, phase in enumerate(modules.get('execution_order', []), 1):
                    console.print(f"  {i}. {phase}")
            
            # Display selected modules by type
            self._display_selected_modules(modules, verbose)
            
            total = self._count_modules(modules)
            console.print(f"\n[green]✓[/green] Module selection complete: {total} total modules")
            console.print("="*80 + "\n")
            
            return modules
            
        except Exception as e:
            console.print(f"\n[red]✗[/red] Module selection failed: {e}")
            console.print("="*80 + "\n")
            return {
                "error": str(e),
                "modules": {
                    "auxiliary": [],
                    "exploit": [],
                    "payload": [],
                    "encoder": [],
                    "nop": [],
                    "post": [],
                    "evasion": [],
                }
            }
    
    def _build_selection_prompt(self, target: str, target_info: dict[str, Any] | None = None) -> str:
        """Build the prompt for module selection.
        
        Args:
            target: Target identifier
            target_info: Additional target information
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a penetration testing expert using Metasploit Framework. 
Analyze the target and recommend specific Metasploit modules to run.

Target: {target}
"""
        
        if target_info:
            prompt += f"\nAdditional Information:\n{json.dumps(target_info, indent=2)}\n"
        
        prompt += """

Based on the target, recommend specific Metasploit modules to test. Consider:

1. **Target Type**: Is it a URL (web app), IP address, hostname, service, etc?
2. **Common Vulnerabilities**: What modules would test for common vulnerabilities?
3. **Reconnaissance**: What auxiliary modules would gather information?
4. **Exploitation**: If vulnerabilities are likely, what exploit modules?
5. **Post-Exploitation**: What post modules might be useful after compromise?
6. **Payloads**: What payloads would be appropriate?
7. **Evasion**: Any evasion techniques needed?
8. **Encoders/NOPs**: Any encoding or NOP requirements?

Provide your recommendations in JSON format with the following structure:
{
  "target_analysis": "Brief analysis of the target and attack approach",
  "execution_order": ["phase1_description", "phase2_description", ...],
  "modules": {
    "auxiliary": [
      {
        "module": "auxiliary/scanner/http/http_version",
        "priority": "high|medium|low",
        "rationale": "Why this module",
        "options": {"key": "value"}
      }
    ],
    "exploit": [
      {
        "module": "exploit/unix/webapp/example",
        "priority": "high|medium|low",
        "rationale": "Why this exploit",
        "options": {"key": "value"},
        "recommended_payload": "payload/generic/shell_reverse_tcp"
      }
    ],
    "payload": [
      {
        "module": "payload/generic/shell_reverse_tcp",
        "priority": "high|medium|low",
        "rationale": "Why this payload",
        "options": {"LHOST": "attacker_ip", "LPORT": "4444"}
      }
    ],
    "post": [
      {
        "module": "post/linux/gather/enum_system",
        "priority": "high|medium|low",
        "rationale": "Why this post module",
        "options": {}
      }
    ],
    "encoder": [],
    "nop": [],
    "evasion": []
  }
}

Important:
- Use real, existing Metasploit module paths
- Prioritize modules based on likelihood of success and information value
- Include proper options for each module where applicable
- For web targets (URLs), focus on web application modules
- For IP addresses, include network scanning and service enumeration
- Only recommend modules that are appropriate for AUTHORIZED security testing
- Be specific and practical

Only respond with valid JSON, no additional text."""
        
        return prompt
    
    def _select_with_openai(self, prompt: str) -> str:
        """Get module selection from OpenAI.
        
        Args:
            prompt: Selection prompt
            
        Returns:
            AI-generated module selection
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert specializing in Metasploit Framework. Provide specific, actionable module recommendations for authorized penetration testing.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        
        return response.choices[0].message.content
    
    def _select_with_anthropic(self, prompt: str) -> str:
        """Get module selection from Anthropic Claude.
        
        Args:
            prompt: Selection prompt
            
        Returns:
            AI-generated module selection
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.2,
            system="You are a cybersecurity expert specializing in Metasploit Framework. Provide specific, actionable module recommendations for authorized penetration testing in JSON format.",
            messages=[{"role": "user", "content": prompt}],
        )
        
        return response.content[0].text
    
    def _parse_selection(self, response: str) -> dict[str, Any]:
        """Parse the AI module selection response.
        
        Args:
            response: Raw response from AI
            
        Returns:
            Parsed module selection dictionary
        """
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            console.print(f"[yellow]⚠[/yellow] Failed to parse AI response: {e}")
            return {
                "error": "Failed to parse AI response",
                "raw_response": response,
                "modules": {
                    "auxiliary": [],
                    "exploit": [],
                    "payload": [],
                    "encoder": [],
                    "nop": [],
                    "post": [],
                    "evasion": [],
                }
            }
    
    def _display_selected_modules(self, selection: dict[str, Any], verbose: bool = True) -> None:
        """Display selected modules in a verbose format.
        
        Args:
            selection: Module selection dictionary
            verbose: Show detailed information
        """
        if "modules" not in selection:
            return
        
        module_types = {
            "auxiliary": ("🔍", "cyan"),
            "exploit": ("💥", "red"),
            "payload": ("📦", "yellow"),
            "post": ("📊", "blue"),
            "encoder": ("🔒", "magenta"),
            "nop": ("⚠️", "white"),
            "evasion": ("🕵️", "green"),
        }
        
        for module_type, (emoji, color) in module_types.items():
            modules = selection["modules"].get(module_type, [])
            if not modules:
                continue
            
            console.print(f"\n[bold {color}]{emoji} {module_type.upper()} MODULES ({len(modules)}):[/bold {color}]")
            
            for i, mod in enumerate(modules, 1):
                priority = mod.get("priority", "low").upper()
                priority_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(priority, "white")
                
                console.print(f"\n  [{priority_color}][{priority}][/{priority_color}] {i}. [bold]{mod.get('module', 'unknown')}[/bold]")
                
                if verbose and mod.get("rationale"):
                    console.print(f"     └─ Rationale: [dim]{mod['rationale']}[/dim]")
                
                if verbose and mod.get("options"):
                    console.print(f"     └─ Options:")
                    for key, value in mod["options"].items():
                        console.print(f"        • {key}: {value}")
                
                if verbose and mod.get("recommended_payload"):
                    console.print(f"     └─ Payload: [yellow]{mod['recommended_payload']}[/yellow]")
    
    def _count_modules(self, selection: dict[str, Any]) -> int:
        """Count total number of modules selected.
        
        Args:
            selection: Module selection dictionary
            
        Returns:
            Total module count
        """
        if "modules" not in selection:
            return 0
        
        count = 0
        for module_type in ["auxiliary", "exploit", "payload", "encoder", "nop", "post", "evasion"]:
            if module_type in selection["modules"]:
                count += len(selection["modules"][module_type])
        
        return count
    
    def filter_by_priority(
        self, 
        selection: dict[str, Any], 
        priority: Literal["high", "medium", "low"] = "high"
    ) -> dict[str, Any]:
        """Filter modules by priority level.
        
        Args:
            selection: Module selection dictionary
            priority: Minimum priority level to include
            
        Returns:
            Filtered selection
        """
        priority_order = {"high": 3, "medium": 2, "low": 1}
        min_priority = priority_order.get(priority, 1)
        
        filtered = {
            "target_analysis": selection.get("target_analysis", ""),
            "execution_order": selection.get("execution_order", []),
            "modules": {}
        }
        
        if "modules" not in selection:
            return filtered
        
        for module_type in ["auxiliary", "exploit", "payload", "encoder", "nop", "post", "evasion"]:
            if module_type in selection["modules"]:
                filtered["modules"][module_type] = [
                    m for m in selection["modules"][module_type]
                    if priority_order.get(m.get("priority", "low"), 1) >= min_priority
                ]
        
        return filtered
