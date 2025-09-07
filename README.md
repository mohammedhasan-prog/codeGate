# CodeGate

A command-line Python security auditor powered by Google's Gemini LLM.

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Configuration

Create a configuration file at `~/.codegate/config.yaml`:

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY"
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

## Usage

Launch the REPL:

```bash
codegate
```

Available commands:

- `scan [file]`: Analyzes a Python file for vulnerabilities.
- `paste`: Enter paste mode to analyze a snippet of code.
- `history`: Show scan history.
- `help`: Show help message.
- `:quit`: Exit the application.
