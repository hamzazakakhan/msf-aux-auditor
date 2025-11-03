"""AI-powered analysis of security scan results."""

from __future__ import annotations

import os
from typing import Any, Literal

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

console = Console()

AIProvider = Literal["openai", "anthropic"]


class AIAnalyzer:
    """Analyze scan results using AI to provide security insights."""
    
    def __init__(
        self, 
        provider: AIProvider = "openai",
        api_key: str | None = None,
        model: str | None = None,
    ):
        """Initialize the AI analyzer.
        
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
            self.model = model or "gpt-4o-mini"
        elif provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def analyze_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze scan results and provide security insights.
        
        Args:
            results: List of scan results from Metasploit modules
            
        Returns:
            Dictionary containing AI analysis with vulnerabilities, 
            recommendations, and risk assessment
        """
        if not results:
            return {
                "analysis": "No scan results to analyze.",
                "vulnerabilities": [],
                "recommendations": [],
                "risk_level": "unknown",
            }
        
        # Prepare the prompt
        prompt = self._build_analysis_prompt(results)
        
        console.print("[blue]🤖[/blue] Analyzing results with AI...")
        
        try:
            # Get analysis from AI
            if self.provider == "openai":
                analysis = self._analyze_with_openai(prompt)
            else:
                analysis = self._analyze_with_anthropic(prompt)
            
            # Parse the analysis
            parsed = self._parse_analysis(analysis)
            
            console.print("[green]✓[/green] AI analysis completed")
            return parsed
            
        except Exception as e:
            console.print(f"[red]✗[/red] AI analysis failed: {e}")
            return {
                "analysis": f"Analysis failed: {e}",
                "vulnerabilities": [],
                "recommendations": [],
                "risk_level": "unknown",
                "error": str(e),
            }
    
    def _build_analysis_prompt(self, results: list[dict[str, Any]]) -> str:
        """Build the prompt for AI analysis.
        
        Args:
            results: Scan results
            
        Returns:
            Formatted prompt string
        """
        prompt = """You are a security analyst reviewing Metasploit auxiliary module scan results. 
Analyze the following scan results and provide:

1. A summary of findings
2. List of potential vulnerabilities identified
3. Risk level assessment (Critical, High, Medium, Low, Info)
4. Specific remediation recommendations
5. Priority actions

Scan Results:
"""
        
        for i, result in enumerate(results, 1):
            prompt += f"\n--- Result {i} ---\n"
            prompt += f"Module: {result.get('module', 'unknown')}\n"
            prompt += f"Target: {result.get('target', 'unknown')}\n"
            prompt += f"Status: {result.get('status', 'unknown')}\n"
            
            if result.get('error'):
                prompt += f"Error: {result.get('error')}\n"
            
            if result.get('result'):
                prompt += f"Details: {result.get('result')}\n"
        
        prompt += """

Please provide your analysis in the following JSON format:
{
  "summary": "Brief overview of findings",
  "vulnerabilities": [
    {
      "title": "Vulnerability name",
      "severity": "Critical|High|Medium|Low|Info",
      "description": "Detailed description",
      "affected_target": "Target identifier"
    }
  ],
  "risk_level": "Critical|High|Medium|Low|Info",
  "recommendations": [
    {
      "priority": "High|Medium|Low",
      "action": "Specific action to take",
      "rationale": "Why this is important"
    }
  ],
  "priority_actions": ["Action 1", "Action 2", ...]
}

Only respond with valid JSON, no additional text.
"""
        
        return prompt
    
    def _analyze_with_openai(self, prompt: str) -> str:
        """Get analysis from OpenAI.
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            AI-generated analysis text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert analyzing penetration test results. Provide detailed, actionable security analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        return response.choices[0].message.content
    
    def _analyze_with_anthropic(self, prompt: str) -> str:
        """Get analysis from Anthropic Claude.
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            AI-generated analysis text
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.3,
            system="You are a cybersecurity expert analyzing penetration test results. Provide detailed, actionable security analysis in JSON format.",
            messages=[{"role": "user", "content": prompt}],
        )
        
        return response.content[0].text
    
    def _parse_analysis(self, analysis: str) -> dict[str, Any]:
        """Parse the AI analysis response.
        
        Args:
            analysis: Raw analysis text from AI
            
        Returns:
            Parsed analysis dictionary
        """
        import json
        
        try:
            # Try to parse as JSON
            parsed = json.loads(analysis)
            return parsed
        except json.JSONDecodeError:
            # If parsing fails, return raw analysis
            return {
                "analysis": analysis,
                "vulnerabilities": [],
                "recommendations": [],
                "risk_level": "unknown",
            }
    
    def summarize_vulnerability(self, vuln_data: dict[str, Any]) -> str:
        """Generate a brief summary for a specific vulnerability.
        
        Args:
            vuln_data: Vulnerability data dictionary
            
        Returns:
            AI-generated summary
        """
        prompt = f"""Provide a brief (2-3 sentence) summary of this vulnerability:

Title: {vuln_data.get('title', 'Unknown')}
Severity: {vuln_data.get('severity', 'Unknown')}
Description: {vuln_data.get('description', 'No description')}

Focus on business impact and immediate risk."""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=150,
                )
                return response.choices[0].message.content
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
        except Exception as e:
            return f"Summary generation failed: {e}"
