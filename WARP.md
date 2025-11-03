# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A CLI tool for running authorized Metasploit auxiliary module scans against target systems. Uses Metasploit RPC to orchestrate scans and generate reports. **Only use on systems you own or have explicit written authorization to test.**

## Development Commands

### Setup

**Linux/Kali:**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv .venv
. .venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Running the CLI

**Start Metasploit RPC first:**
```bash
# Start msfrpcd (required before running scans)
msfrpcd -P <password> -U msf -a 127.0.0.1
```

**Basic commands:**
```bash
# Show help
python -m msf_aux_auditor --help

# Show version
python -m msf_aux_auditor version

# Show info
python -m msf_aux_auditor info
```

**Scanning:**
```bash
# Create your configuration file
cp aux_modules.sample.json aux_modules.json
# Edit aux_modules.json with your RPC password and allowed modules

# Run scan with all configured modules
python -m msf_aux_auditor scan <target_ip>

# Run specific module
python -m msf_aux_auditor scan <target_ip> --module auxiliary/scanner/portscan/tcp

# Save results to file
python -m msf_aux_auditor scan <target_ip> --output results.json
python -m msf_aux_auditor scan <target_ip> --output results.yaml
python -m msf_aux_auditor scan <target_ip> --output results.txt

# Use custom config file
python -m msf_aux_auditor scan <target_ip> --config my_config.json
```

## Architecture

### Package Structure
- **src/msf_aux_auditor/**: Main package directory
  - `__init__.py`: Package initialization and version definition
  - `__main__.py`: Entry point for `-m` execution
  - `cli.py`: Typer-based CLI with commands (version, info, scan)
  - `config.py`: Configuration loading and validation using Pydantic
  - `msf_client.py`: Metasploit RPC client wrapper for running auxiliary modules
  - `reporter.py`: Report generation (JSON, YAML, text formats)

### Key Technologies
- **Typer**: CLI framework for command-line interface
- **Rich**: Terminal formatting and styled output (Console, Panel, Table)
- **Pydantic**: Data validation for configuration
- **pymetasploit3**: Python library for Metasploit RPC communication
- **PyYAML**: YAML report generation

### Current Implementation

**CLI Commands:**
- `version`: Displays package version
- `info`: Shows usage information and warnings
- `scan`: Executes Metasploit auxiliary modules against targets

**Workflow:**
1. Load configuration from JSON file (modules list, RPC settings)
2. Connect to Metasploit RPC server (msfrpcd)
3. Execute configured auxiliary modules against target
4. Collect and display results
5. Optionally save reports in multiple formats

### Configuration

**Configuration file format** (`aux_modules.json`):
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

- `allowed_modules`: List of Metasploit auxiliary modules to run (must start with `auxiliary/`)
- `msf_config`: Metasploit RPC connection settings
- `timeout`: Module execution timeout in seconds

## Important Context

**Legal and Ethical Usage:**
- Only use on systems you own or have explicit written authorization to test
- Unauthorized security testing may be illegal in your jurisdiction
- This tool requires Metasploit Framework and msfrpcd to be installed and running
- Always follow responsible disclosure practices

**Prerequisites:**
- Metasploit Framework installed (typically pre-installed on Kali Linux)
- msfrpcd running with configured password
- Python 3.10+

## Python Requirements
- Python 3.10+
- Dependencies: typer>=0.12, rich>=13.7, pydantic>=2.8, pymetasploit3>=1.0.0, PyYAML>=6.0

## Common Metasploit Auxiliary Modules

**Port Scanning:**
- `auxiliary/scanner/portscan/tcp` - TCP port scanner
- `auxiliary/scanner/portscan/syn` - SYN port scanner

**Service Detection:**
- `auxiliary/scanner/http/http_version` - HTTP version detection
- `auxiliary/scanner/ssh/ssh_version` - SSH version detection
- `auxiliary/scanner/ftp/ftp_version` - FTP version detection
- `auxiliary/scanner/smb/smb_version` - SMB version detection

**Vulnerability Scanning:**
- `auxiliary/scanner/http/ssl` - SSL/TLS scanner
- `auxiliary/scanner/smb/smb_ms17_010` - EternalBlue detector
