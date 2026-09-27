# hackerearth-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-v0.2.0-orange.svg)](https://github.com/pratham-jain33/hackerearth-mcp/releases)
[![PyPI](https://img.shields.io/pypi/v/hackerearth-mcp.svg)](https://pypi.org/project/hackerearth-mcp/)
[![Stars](https://img.shields.io/github/stars/pratham-jain33/hackerearth-mcp.svg)](https://github.com/pratham-jain33/hackerearth-mcp/stargazers)
[![Tests](https://github.com/pratham-jain33/hackerearth-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/pratham-jain33/hackerearth-mcp/actions)

Give any AI assistant a code **run button**.

> **Unofficial community project.** Not made by, endorsed by, or affiliated with HackerEarth. You bring your own free HackerEarth API key.

## Why

AI assistants are great at writing code and terrible at knowing whether it works. They guess. This server plugs into any MCP-compatible assistant (Claude Desktop, Claude Code, Cursor, and more) and lets it **actually run code** in 24 programming languages on HackerEarth's sandboxed servers, then read the real output. No local toolchains to install. Nothing untrusted ever touches your machine.

## Tools

| Tool | Description |
|------|-------------|
| `run_code` | Sends code plus a language to HackerEarth, waits for it to run, and returns the printed output and any error messages. |
| `list_languages` | Lists every language HackerEarth can run, with the exact identifiers to pass to `run_code`. Takes no inputs. |

## Quickstart

**1. Get a free HackerEarth API key**

Register a client in the [HackerEarth developer dashboard](https://www.hackerearth.com) to receive a `client-secret`. The free tier includes a generous request quota.

**2. Install**

No cloning needed:

```bash
uvx hackerearth-mcp
```

or with pip:

```bash
pip install hackerearth-mcp
```

From source instead:

```bash
git clone https://github.com/pratham-jain33/hackerearth-mcp
cd hackerearth-mcp
python -m venv .venv
.venv/bin/pip install -e .
```

**3. Connect your assistant**

Claude Desktop config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hackerearth": {
      "command": "uvx",
      "args": ["hackerearth-mcp"],
      "env": {
        "HACKEREARTH_KEY": "paste-your-client-secret-here"
      }
    }
  }
}
```

From source, point at your checkout instead:

```json
{
  "mcpServers": {
    "hackerearth": {
      "command": "/absolute/path/to/hackerearth-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/hackerearth-mcp/server.py"],
      "env": {
        "HACKEREARTH_KEY": "paste-your-client-secret-here"
      }
    }
  }
}
```

Restart Claude Desktop, then try: *"run this Python program and tell me what it prints: `print(6 * 7)`"*

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `HACKEREARTH_KEY` | Yes | Your HackerEarth `client-secret`. Read from the environment, never hardcoded, never sent to the assistant in chat. |

## How it works

*(This section is written by the project's author.)*

1. You ask the assistant to run some code.
2. The assistant calls `run_code` with the code and the language.
3. The server sends it to HackerEarth with your key and gets back a tracking token.
4. The server polls HackerEarth until the run finishes.
5. HackerEarth runs the code in a sealed sandbox on their machines.
6. The server hands the output back to the assistant, which explains it to you.

## Example session

```
You:    Is this Fibonacci function correct? Run it and show me the first 10 numbers.
        def fib(n):
            a, b = 0, 1
            for _ in range(n):
                print(a, end=" ")
                a, b = b, a + b
        fib(10)

Claude: [calls run_code with your function]
        It works. The output is: 0 1 1 2 3 5 8 13 21 34
```

## Roadmap

- [x] v0.1 — code submission, status polling, output download, compile/runtime error reporting, 24-language list
- [x] v0.2 — PyPI packaging, install and run with a single `uvx hackerearth-mcp` command, `server.json` for the official MCP registry
- [ ] Submission to the official MCP registry and community directories

## Contributing

Issues and pull requests are welcome. If you add a tool, write its description the way you'd explain it to a smart friend who has never seen it — the assistant reads that text to decide when to use it.

## License

MIT © Pratham Jain. See [LICENSE](LICENSE).

## Acknowledgments

Built on [HackerEarth's](https://www.hackerearth.com) code execution API and the [Model Context Protocol](https://modelcontextprotocol.io/). Thanks to HackerEarth for a genuinely developer-friendly free tier.
