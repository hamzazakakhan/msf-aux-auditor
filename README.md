# msf-aux-auditor

A CLI tool for running authorized Metasploit auxiliary module scans against target systems.

## Important - Legal Notice

**⚠️ AUTHORIZATION REQUIRED**
- Use ONLY on systems you own or have explicit written authorization to test
- Unauthorized security testing is illegal in most jurisdictions
- Always follow responsible disclosure practices
- The maintainers do not accept liability for misuse

## Overview

This tool orchestrates Metasploit modules via RPC to perform authorized security assessments. It provides:
- **AI-Powered Module Selection**: Automatically selects appropriate modules based on target analysis
- **Universal Module Support**: Auxiliaries, exploits, payloads, encoders, NOPs, post-exploitation, evasion
- **Intelligent Analysis**: AI-driven vulnerability assessment and recommendations
- **Configuration-based execution**: Manual or AI-assisted module selection
- **Multiple report formats**: JSON, YAML, text with AI insights
- **Verbose output**: Detailed execution logging and progress tracking

## Installation

### Quick Install (Kali Linux / Linux)

```bash
# Clone the repository
git clone https://github.com/hamzazakakhan/msf-aux-auditor.git
cd msf-aux-auditor

# Install as a command
pip install -e .
```

After installation, use the commands:
```bash
msf-aux-auditor --help
msf-auditor --help  # shorter alias
```

**See [INSTALL.md](INSTALL.md) for detailed installation instructions.**

## Prerequisites

- Python 3.10+
- Metasploit Framework (pre-installed on Kali Linux)
- msfrpcd running and configured
- OpenAI API key or Anthropic API key (for AI features)

## Quick Start

### 1. Setup Environment

**Linux/Kali:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

### 2. Start Metasploit RPC

```bash
msfrpcd -P your_password -U msf -a 127.0.0.1
```

### 3. Configure

```bash
cp aux_modules.sample.json aux_modules.json
# Edit aux_modules.json with your RPC password and desired modules
```

### 4. Configure AI (Optional)

For AI-powered module selection:

```bash
# Set API key as environment variable
export OPENAI_API_KEY="your-api-key"
# or
export ANTHROPIC_API_KEY="your-api-key"
```

Or add to `aux_modules.json`:

```json
{
  "ai_config": {
    "enabled": true,
    "provider": "openai",
    "api_key": "your-api-key",
    "model": "gpt-4o"
  }
}
```

### 5. Run Scans

**AI-Powered Scanning (Recommended):**

```bash
# AI selects and runs appropriate modules
msf-aux-auditor ai-scan <target>

# AI scan with high priority modules only
msf-aux-auditor ai-scan https://example.com --priority high

# Auto-run without confirmation
msf-aux-auditor ai-scan 192.168.1.100 --auto-run

# Save results with AI analysis
msf-aux-auditor ai-scan example.com --output report.json
```

**Manual Scanning:**

```bash
# Scan with configured modules
msf-aux-auditor scan <target_ip>

# Scan with specific module
msf-aux-auditor scan <target_ip> --module auxiliary/scanner/portscan/tcp

# Save results
msf-aux-auditor scan <target_ip> --output results.json
```

*Note: If not installed, use `python -m msf_aux_auditor` instead of `msf-aux-auditor`*

## Configuration

Edit `aux_modules.json`:

```json
{
  "allowed_modules": [],
  "msf_config": {
    "host": "127.0.0.1",
    "port": 55553,
    "username": "msf",
    "password": "your_rpc_password",
    "ssl": false
  },
  "ai_config": {
    "enabled": true,
    "provider": "openai",
    "api_key": "",
    "model": "gpt-4o"
  },
  "timeout": 300
}
```

### Configuration Options

**AI Config:**
- **provider**: `"openai"` or `"anthropic"`
- **api_key**: Your API key (or use environment variables)
- **model**: Model to use (defaults: `gpt-4o` for OpenAI, `claude-3-5-sonnet-20241022` for Anthropic)
- **enabled**: Enable AI analysis of scan results

**Module Config:**
- **allowed_modules**: Leave empty `[]` for AI auto-selection, or add specific modules for manual `scan` command

## Features

### AI-Powered Module Selection

The AI analyzes your target and automatically recommends:
- **Reconnaissance modules**: Information gathering and enumeration
- **Vulnerability scanners**: Targeted auxiliary modules
- **Exploits**: Appropriate exploitation modules
- **Payloads**: Suitable payloads for the target platform
- **Post-exploitation**: Modules for after successful compromise
- **Evasion techniques**: Anti-detection methods
- **Encoders/NOPs**: As needed for exploit delivery

### Verbose Execution

Detailed output includes:
- Target analysis and attack strategy
- Module selection rationale
- Execution phases and progress
- Real-time module status
- AI-driven vulnerability insights
- Remediation recommendations

### Supported Module Types

- 🔍 **Auxiliary**: Scanners, fuzzers, and information gathering
- 💥 **Exploits**: Vulnerability exploitation
- 📦 **Payloads**: Shell, Meterpreter, and custom payloads
- 📊 **Post**: Post-exploitation and privilege escalation
- 🔒 **Encoders**: Payload encoding for evasion
- ⚠️ **NOPs**: NOP sleds for exploit reliability
- 🕵️ **Evasion**: Anti-detection and anti-forensics

## Ethics and Legal

Penetration testing requires prior written authorization. Misuse may be illegal. Always:
- Obtain written permission before testing
- Stay within the defined scope
- Document all activities
- Follow responsible disclosure for any findings
- Use AI responsibly and verify recommendations
