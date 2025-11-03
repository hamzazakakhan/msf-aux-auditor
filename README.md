# msf-aux-auditor

A CLI tool for running authorized Metasploit auxiliary module scans against target systems.

## Important - Legal Notice

**⚠️ AUTHORIZATION REQUIRED**
- Use ONLY on systems you own or have explicit written authorization to test
- Unauthorized security testing is illegal in most jurisdictions
- Always follow responsible disclosure practices
- The maintainers do not accept liability for misuse

## Overview

This tool orchestrates Metasploit auxiliary modules via RPC to perform authorized security assessments. It provides:
- Configuration-based module execution
- Multiple report output formats (JSON, YAML, text)
- Structured scanning workflow
- Safe, controlled testing environment

## Prerequisites

- Python 3.10+
- Metasploit Framework (pre-installed on Kali Linux)
- msfrpcd running and configured

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

### 4. Run Scans

```bash
# Scan with configured modules
python -m msf_aux_auditor scan <target_ip>

# Scan with specific module
python -m msf_aux_auditor scan <target_ip> --module auxiliary/scanner/portscan/tcp

# Save results
python -m msf_aux_auditor scan <target_ip> --output results.json
```

## Configuration

Edit `aux_modules.json`:

```json
{
  "allowed_modules": [
    "auxiliary/scanner/portscan/tcp",
    "auxiliary/scanner/http/http_version"
  ],
  "msf_config": {
    "host": "127.0.0.1",
    "port": 55553,
    "username": "msf",
    "password": "your_rpc_password",
    "ssl": false
  },
  "timeout": 300
}
```

## Ethics and Legal

Penetration testing requires prior written authorization. Misuse may be illegal. Always:
- Obtain written permission before testing
- Stay within the defined scope
- Document all activities
- Follow responsible disclosure for any findings
