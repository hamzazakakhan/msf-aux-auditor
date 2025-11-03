# Installation Guide

## Quick Install (Recommended)

### On Kali Linux / Linux

```bash
# Clone the repository
git clone https://github.com/hamzazakakhan/msf-aux-auditor.git
cd msf-aux-auditor

# Install with pip (creates command-line tools)
pip install -e .

# Or install from source
pip install .
```

After installation, you can use these commands anywhere:

```bash
msf-aux-auditor --help
msf-auditor --help  # shorter alias
```

### On Windows

```powershell
# Clone the repository
git clone https://github.com/hamzazakakhan/msf-aux-auditor.git
cd msf-aux-auditor

# Install with pip
pip install -e .
```

## Installation Options

### Development Installation

Install in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

This allows you to modify the code and see changes immediately.

### System-Wide Installation

```bash
sudo pip install .
```

### User Installation

```bash
pip install --user .
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows

# Install
pip install -e .
```

## Available Commands After Installation

Once installed, you'll have these commands available:

```bash
# Main command
msf-aux-auditor --help

# Shorter alias
msf-auditor --help

# Show version
msf-aux-auditor version

# Show info
msf-aux-auditor info

# Run AI-powered scan
msf-aux-auditor ai-scan <target>

# Run manual scan
msf-aux-auditor scan <target>
```

## Verifying Installation

```bash
# Check if installed
which msf-aux-auditor

# Check version
msf-aux-auditor version

# Test help
msf-aux-auditor --help
```

Expected output:
```
Usage: msf-aux-auditor [OPTIONS] COMMAND [ARGS]...

  Non-operational scaffold for authorized auditing workflows.

Options:
  --help  Show this message and exit.

Commands:
  ai-scan  AI-powered module selection and scanning.
  info     Show important usage information.
  scan     Run auxiliary scans against target.
  version  Show version.
```

## Configuration

After installation, set up your configuration:

```bash
# Copy sample config
cp aux_modules.sample.json aux_modules.json

# Edit config
nano aux_modules.json  # or vim, code, etc.
```

Edit the configuration file:

```json
{
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
  }
}
```

Set API keys:

```bash
# Set OpenAI key
export OPENAI_API_KEY="sk-..."

# Or Anthropic key
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Dependencies

The tool automatically installs these dependencies:

- `typer>=0.12` - CLI framework
- `rich>=13.7` - Terminal formatting
- `pydantic>=2.8` - Data validation
- `pymetasploit3>=1.0.0` - Metasploit RPC client
- `PyYAML>=6.0` - YAML support
- `openai>=1.0.0` - OpenAI API
- `anthropic>=0.18.0` - Anthropic API

## System Requirements

- Python 3.10 or higher
- Metasploit Framework
- msfrpcd running (for scanning)
- Internet connection (for AI features)
- OpenAI or Anthropic API key (for AI features)

## Kali Linux Specific Setup

On Kali Linux, Metasploit is pre-installed. Just start the RPC server:

```bash
# Start Metasploit RPC
msfrpcd -P your_password -U msf -a 127.0.0.1

# In another terminal, use the tool
msf-aux-auditor ai-scan example.com
```

## Troubleshooting

### Command Not Found

If `msf-aux-auditor` is not found after installation:

```bash
# Check pip install location
pip show msf-aux-auditor

# Ensure ~/.local/bin is in PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission Denied

```bash
# Use user install instead of system
pip install --user .
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall .
```

### Module Not Found

```bash
# Check Python version
python3 --version  # Must be 3.10+

# Reinstall with correct Python
python3.10 -m pip install .
```

## Uninstallation

```bash
pip uninstall msf-aux-auditor
```

## Updating

```bash
# Pull latest changes
git pull origin master

# Reinstall
pip install --upgrade .
```

## From GitHub Releases (Future)

Once published to PyPI:

```bash
pip install msf-aux-auditor
```

## Docker Installation (Optional)

```bash
# Build Docker image
docker build -t msf-aux-auditor .

# Run
docker run -it msf-aux-auditor msf-auditor --help
```

## Manual Installation

If you prefer not to use pip:

```bash
# Clone repository
git clone https://github.com/hamzazakakhan/msf-aux-auditor.git
cd msf-aux-auditor

# Install dependencies
pip install -r requirements.txt

# Run directly
python -m msf_aux_auditor --help
```

## Support

For installation issues:
1. Check Python version: `python3 --version`
2. Check pip version: `pip --version`
3. Verify virtual environment is activated
4. Check GitHub issues: https://github.com/hamzazakakhan/msf-aux-auditor/issues
