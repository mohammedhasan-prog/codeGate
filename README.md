# CodeGate

A comprehensive Python security auditor powered by Google's Gemini LLM with both CLI and Web interfaces.

## Features

- 🔍 **Static Code Analysis** - Detects security issues, code smells, and complexity problems
- 🤖 **AI-Powered Security Analysis** - Uses Google Gemini to identify vulnerabilities
- ⚡ **Real-time Scanning** - Fast analysis with caching support
- 📊 **Risk Assessment** - Comprehensive risk scoring and reporting
- 💻 **CLI Interface** - Interactive REPL for terminal users
- 🌐 **Web Interface** - Modern, responsive web UI with real-time progress updates
- 📝 **Scan History** - Track and review past security audits
- 🎯 **Multiple Detection Categories** - Command injection, SQL injection, path traversal, cryptographic issues, and more

## Installation

```bash
# Clone the repository
git clone https://github.com/001Priyans/codeGate.git
cd codeGate

# Create and activate virtual environment (recommended)
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CodeGate
python setup.py install
```

## Configuration

Create a configuration file at `~/.codegate/config.yaml`:

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY"  # Get from https://makersuite.google.com/app/apikey
  model: "gemini-1.5-pro"
  temperature: 0.1
  max_tokens: 4000

settings:
  save_history: true
  history_path: "~/.codegate/history.json"
  enable_caching: true
  cache_duration: 24

output:
  colored: true
  verbose: false
```

Or set your API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Usage

### CLI Interface

Launch the interactive REPL:

```bash
codegate
```

Available commands:

- `scan [file]`: Analyzes a Python file for vulnerabilities
- `paste`: Enter paste mode to analyze a code snippet
- `history`: Show scan history
- `help`: Show help message
- `:quit`: Exit the application

**Example:**
```bash
codegate
> scan vulnerable_code.py
> paste
# ... paste your code ...
# Press Ctrl+D to finish
```

### Web Interface

Start the web server:

```bash
python src/codegate/web/launcher.py
```

Or with custom options:

```bash
python src/codegate/web/launcher.py --host 0.0.0.0 --port 5000 --public
```

Then open your browser to `http://localhost:5000`

**Web Interface Features:**
- 📝 Interactive code editor with syntax highlighting
- 📊 Real-time progress updates during analysis
- 🎨 Beautiful, responsive UI
- 📈 Visual risk assessment charts
- 🔍 Detailed vulnerability reports
- 📜 Scan history with filtering
- 💾 Export reports

## Vulnerability Detection

CodeGate detects the following security issues:

1. **Command Injection** - `os.system`, `subprocess` with `shell=True`, `eval`, `exec`
2. **Path Traversal** - File operations with user input, `../` patterns
3. **SQL Injection** - Raw SQL string construction
4. **Deserialization** - `pickle.loads`, `yaml.load` without `safe_load`
5. **Cryptographic Issues** - Weak algorithms, hardcoded keys, bad randomness
6. **Information Disclosure** - Sensitive data in logs/errors, debug info
7. **Resource Exhaustion** - Infinite loops, fork bombs, unbounded allocations
8. **Network Security** - Unvalidated URLs, insecure connections
9. **Input Validation** - Missing sanitization, buffer overflows
10. **Dependency Issues** - Known vulnerable packages

## Example Output

```
╭──────────────────────────────────────────────────────────╮
│           CodeGate Security Analysis Report              │
╰──────────────────────────────────────────────────────────╯

📄 File: vulnerable_code.py
🗓️  Analyzed: 2025-10-22 08:30:15
⏱️  Duration: 5.2s
📏 Lines: 45

🎯 Risk Score: 85/100 (HIGH RISK)

⚠️  VULNERABILITIES FOUND: 3

1. Command Injection [CRITICAL]
   Line 12: os.system(user_input)
   Impact: Arbitrary command execution
   Fix: Use subprocess with list arguments, avoid shell=True

2. SQL Injection [HIGH]
   Line 25: cursor.execute(f"SELECT * FROM users WHERE id={user_id}")
   Impact: Database compromise
   Fix: Use parameterized queries

3. Weak Cryptography [MEDIUM]
   Line 38: hashlib.md5(password)
   Impact: Weak password hashing
   Fix: Use bcrypt or argon2
```

## Development

### Project Structure

```
codeGate/
├── src/codegate/
│   ├── cli/              # CLI interface
│   ├── core/             # Core analysis engines
│   │   ├── gemini_analyzer.py
│   │   ├── static_analyzer.py
│   │   ├── risk_engine.py
│   │   └── preprocessor.py
│   ├── utils/            # Utilities
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── history.py
│   │   └── helpers.py
│   └── web/              # Web interface
│       ├── app.py
│       ├── launcher.py
│       ├── static/
│       └── templates/
├── tests/                # Test files
└── examples/             # Example vulnerable code
```

### Running Tests

```bash
python -m pytest tests/
```

## Troubleshooting

### Web Interface Not Loading

If the web interface gets stuck at "Preparing code for analysis...":
- Check that your Gemini API key is valid
- Ensure eventlet is properly installed
- See `WEB_INTERFACE_FIXES.md` for detailed troubleshooting

### API Key Issues

```bash
# Check if API key is configured
python -c "from src.codegate.utils.config import config_manager; print(config_manager.get('gemini.api_key'))"
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


## Security Note

CodeGate is a security analysis tool and should be used responsibly. Always review the findings and apply fixes carefully. This tool is meant to assist developers, not replace security experts.
