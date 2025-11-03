# AI-Powered Features Guide

## Overview

The AI integration enables intelligent, automated selection of Metasploit modules based on target analysis. The AI analyzes your target (URL, IP, hostname, etc.) and automatically recommends appropriate modules from all categories:

- 🔍 **Auxiliary** - Scanners, enumeration, information gathering
- 💥 **Exploits** - Vulnerability exploitation modules
- 📦 **Payloads** - Shells, Meterpreter, custom payloads
- 📊 **Post** - Post-exploitation and privilege escalation
- 🔒 **Encoders** - Payload encoding for evasion
- ⚠️ **NOPs** - NOP sleds for exploit reliability
- 🕵️ **Evasion** - Anti-detection techniques

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

**Option A: Environment Variables (Recommended)**

```bash
# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option B: Configuration File**

Edit `aux_modules.json`:

```json
{
  "ai_config": {
    "enabled": true,
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4o"
  }
}
```

### 3. Start Metasploit RPC

```bash
msfrpcd -P your_password -U msf -a 127.0.0.1
```

## Usage

### Basic AI Scan

```bash
python -m msf_aux_auditor ai-scan <target>
```

Example:
```bash
# Scan a web application
python -m msf_aux_auditor ai-scan https://example.com

# Scan an IP address
python -m msf_aux_auditor ai-scan 192.168.1.100

# Scan a hostname
python -m msf_aux_auditor ai-scan server.local
```

### Advanced Options

**Filter by Priority**

```bash
# Only run high-priority modules
python -m msf_aux_auditor ai-scan example.com --priority high

# Include medium and high priority
python -m msf_aux_auditor ai-scan example.com --priority medium

# Run all recommended modules
python -m msf_aux_auditor ai-scan example.com --priority low
```

**Auto-Run Mode**

```bash
# Skip confirmation prompt
python -m msf_aux_auditor ai-scan example.com --auto-run
```

**Save Results**

```bash
# JSON output with AI analysis
python -m msf_aux_auditor ai-scan example.com --output report.json

# YAML format
python -m msf_aux_auditor ai-scan example.com --output report.yaml

# Text format
python -m msf_aux_auditor ai-scan example.com --output report.txt
```

**Custom Configuration**

```bash
python -m msf_aux_auditor ai-scan example.com --config custom_config.json
```

## How It Works

### 1. Target Analysis

The AI analyzes the target to determine:
- Target type (web app, network service, etc.)
- Likely technologies and platforms
- Appropriate attack vectors
- Reconnaissance needs

### 2. Module Selection

Based on analysis, the AI recommends:
- **Reconnaissance phase**: Information gathering modules
- **Vulnerability scanning**: Targeted auxiliary modules
- **Exploitation**: Appropriate exploit modules
- **Payload delivery**: Compatible payloads
- **Post-exploitation**: Privilege escalation and data gathering
- **Evasion**: Anti-detection techniques

### 3. Verbose Execution

Each module execution shows:
- Module type and full path
- Configuration options
- Rationale for selection
- Real-time progress
- Execution results

### 4. AI Analysis

After execution, AI provides:
- Vulnerability summary
- Risk assessment (Critical/High/Medium/Low)
- Specific recommendations
- Priority actions
- Remediation steps

## Example Output

```
================================================================================
🤖 AI-POWERED MODULE SELECTION
================================================================================

Target: https://example.com

→ Analyzing target characteristics...
→ Consulting AI (openai/gpt-4o)...

📊 TARGET ANALYSIS:
The target is a web application. Recommended approach includes reconnaissance,
web vulnerability scanning, and common web exploit attempts.

📋 RECOMMENDED EXECUTION ORDER:
  1. Information Gathering Phase
  2. Web Application Scanning
  3. Service Enumeration
  4. Vulnerability Exploitation (if applicable)

🔍 AUXILIARY MODULES (3):

  [HIGH] 1. auxiliary/scanner/http/http_version
     └─ Rationale: Identify web server version and technology stack
     └─ Options:
        • RHOSTS: example.com
        • RPORT: 443

  [HIGH] 2. auxiliary/scanner/http/dir_scanner
     └─ Rationale: Discover hidden directories and files
     └─ Options:
        • RHOSTS: example.com

  [MEDIUM] 3. auxiliary/scanner/ssl/ssl_version
     └─ Rationale: Check SSL/TLS configuration and vulnerabilities
     └─ Options:
        • RHOSTS: example.com
        • RPORT: 443

✓ Module selection complete: 3 total modules
================================================================================

Run 3 selected modules against https://example.com?
Continue [y/n]: y

→ Connecting to Metasploit RPC...
  • Host: 127.0.0.1
  • Port: 55553
  • User: msf
✓ Connected to Metasploit at 127.0.0.1:55553

================================================================================
EXECUTING MODULE
================================================================================
Type: auxiliary
Module: auxiliary/scanner/http/http_version
Target: example.com

→ Loading module...
✓ Module loaded: auxiliary/scanner/http/http_version
Description: Detect HTTP server version and headers

→ Setting target: RHOSTS=example.com

→ Configuring module options:
  • RPORT = 443

Available Options:
  * RHOSTS: example.com
    HTTP target host(s)
  * RPORT: 443
    HTTP target port

▶ EXECUTING MODULE...
✓ Module execution initiated
⠋ Running module... (3s)
✓ Job 1 completed

✓ Module completed in 3.45s
================================================================================

✓ Module 1 completed successfully
...
```

## Best Practices

### 1. Target Specification

Be specific with your target:
- **Good**: `https://app.example.com:8443`
- **Good**: `192.168.1.50`
- **Avoid**: Just `example` (ambiguous)

### 2. Priority Selection

- **High priority**: Quick, safe reconnaissance and common vulnerabilities
- **Medium priority**: More thorough scanning, some risk
- **Low priority**: Comprehensive testing, may trigger detection

### 3. Authorization

**CRITICAL**: Only scan targets you own or have written authorization to test.
- Document authorization before scanning
- Stay within defined scope
- Log all activities
- Report findings responsibly

### 4. Review Before Running

Without `--auto-run`, review the AI-selected modules before executing:
- Verify modules are appropriate
- Check module options
- Ensure you're targeting the correct host
- Confirm authorization

### 5. AI Verification

AI recommendations should be reviewed:
- Verify modules exist in your Metasploit version
- Confirm options are correct for your target
- Cross-reference with manual analysis
- Don't blindly trust AI suggestions

## Troubleshooting

### AI Selection Fails

```
Error: Module selection failed
```

**Solutions**:
- Check API key is valid
- Verify internet connectivity
- Try different AI provider
- Check API quota/limits

### Module Not Found

```
Error: Module 'auxiliary/...' not found or invalid
```

**Solutions**:
- Update Metasploit: `msfupdate`
- Verify module path in msfconsole
- Check module is available in your version
- Try alternative modules

### Connection Refused

```
Error: Failed to connect to Metasploit RPC
```

**Solutions**:
- Ensure msfrpcd is running
- Check RPC credentials in config
- Verify host/port settings
- Check firewall settings

## Configuration Reference

### AI Config Options

```json
{
  "ai_config": {
    "enabled": true,           // Enable AI analysis of results
    "provider": "openai",      // "openai" or "anthropic"
    "api_key": "",            // API key (optional if using env vars)
    "model": "gpt-4o"         // Model to use
  }
}
```

### Supported Models

**OpenAI**:
- `gpt-4o` (recommended, default)
- `gpt-4o-mini` (faster, cheaper)
- `gpt-4-turbo`

**Anthropic**:
- `claude-3-5-sonnet-20241022` (recommended, default)
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`

## Advanced Usage

### Custom Target Info

Provide additional context for better module selection:

```bash
# In Python script
from msf_aux_auditor.ai_module_selector import AIModuleSelector

selector = AIModuleSelector(provider="openai")
selection = selector.select_modules(
    target="192.168.1.100",
    target_info={
        "services": ["http", "ssh", "ftp"],
        "os": "Linux",
        "notes": "Development server"
    }
)
```

### Programmatic Usage

```python
from msf_aux_auditor.config import load_config
from msf_aux_auditor.ai_module_selector import AIModuleSelector
from msf_aux_auditor.msf_runner import UniversalMsfRunner

# Load config
cfg = load_config("aux_modules.json")

# Select modules
selector = AIModuleSelector(
    provider=cfg.ai_config.provider,
    api_key=cfg.ai_config.api_key
)
selection = selector.select_modules("example.com", verbose=True)

# Run modules
runner = UniversalMsfRunner(cfg.msf_config, verbose=True)
runner.connect()

for mod in selection["modules"]["auxiliary"]:
    runner.run_module(
        module_type="auxiliary",
        module_path=mod["module"],
        target="example.com",
        options=mod.get("options", {})
    )

runner.disconnect()
```

## Security Considerations

1. **API Keys**: Store securely, use environment variables
2. **Logging**: AI queries may contain target information
3. **Data Privacy**: Target data is sent to AI providers
4. **Rate Limits**: Be aware of API usage limits
5. **Cost**: AI API calls cost money per request

## Support

For issues or questions:
1. Check this documentation
2. Review error messages
3. Verify configuration
4. Check Metasploit logs
5. Test manual module execution

## Legal Disclaimer

This tool is for authorized security testing only. Unauthorized use is illegal.
The AI provides suggestions but does not guarantee safety or legality.
Always verify you have proper authorization before testing any target.
