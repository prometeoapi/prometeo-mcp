# Prometeo MCP Server

A server implementation for MCP (Modular Control Platform) to connect Prometeo API. Include functions to access banking information, validate accounts and query CURP.

---

## 🚀 Features

- ✅ Python 3.11+
- ✅ Pydantic v2.x with `ConfigDict`
- ✅ `mcp[cli] >= 1.6.0` integration
- ✅ Prometeo API SDK v2.0.1

---

## 📦 Requirements

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) installed globally

---

## 📥 Installation

Clone the repository and install dependencies with `uv`:

```bash
git clone https://github.com/prometeoapi/prometeo-mcp.git
cd prometeo-mcp
uv venv
source .venv/bin/activate
```

Install dependencies (you can skip this step if you're running `uv run` directly inside an MCP-compatible LLM environment like Claude Desktop):

```bash
uv pip install -e .
```

## 🧠 Running the Application in MCP-Compatible LLMs

This project supports MCP (Multi-agent Control Protocol) integration and can be configured for execution inside LLM tools or agents that support external server launching.

Below are configuration examples for different LLMs:

### 🤖 Claude Desktop (Anthropic)

Inside the Claude Desktop JSON config, add or extend the mcpServers section like this:

```json
{
  "mcpServers": {
    "PrometeoAPI": {
      "command": "uv",
      "args": [
        "--directory",
        "/your/path/to/host",
        "run",
        "prometeo_mcp/server.py"
      ],
      "env": {
        "PROMETEO_API_KEY": "your_api_key",
        "PROMETEO_ENVIRONMENT": "sandbox"
      }
    }
  }
}
```

> Replace /your/path/to/host with the full absolute path on your system.
>
> Replace your_api_key with your Prometeo sandbox or production key.
>


### 🧠 OpenAI GPTs (via Plugins or Tool Use)

For GPTs that support calling tools via process launch (or via Agent toolchains like LangChain, AutoGen, etc.), use this shell command:

```bash
uv run prometeo_mcp/server.py
```

You can wrap this in a tool definition or ToolExecutor.

#### 🕹️ OpenInterpreter / OpenDevin

```json
{
  "tools": {
    "PrometeoServer": {
      "type": "command",
      "exec": "uv",
      "args": [
        "run",
        "prometeo_mcp/server.py"
      ],
      "cwd": "/your/path/to/host",
      "env": {
        "PROMETEO_API_KEY": "your_api_key",
        "PROMETEO_ENVIRONMENT": "sandbox"
      }
    }
  }
}
```

> Replace /your/path/to/host with the full absolute path on your system.
>
> Replace your_api_key with your Prometeo sandbox or production key.
>

#### 🧪 LangChain (via Runnable or Tool)

For LangChain custom tools:

```python
from langchain.tools import Tool

prometeo_server_tool = Tool.from_function(
    name="PrometeoServer",
    func=lambda x: os.system("uv run mcp/server.py"),
    description="Runs Prometeo API server"
)
```

---

### 💡 Prompt Examples

To see how to interact with this MCP server via supported LLMs, check out:

📁 [`examples/prompts.txt`](examples/prompts.txt)

It contains example prompts you can copy and paste into Claude, ChatGPT (with MCP), or any other compatible LLM to trigger real server calls and test behavior.


---

## 🧪 Running Tests

This project uses pytest and pytest-asyncio:

```bash
pytest
```

Make sure async tests are marked with @pytest.mark.asyncio.

---

##  🛠 Development

Activate the virtual environment:

```bash
source .venv/bin/activate
uv pip install -e .[dev]
```

Run the application:

```bash
uv run prometeo_mcp/server.py
```

## 📄 License

MIT License. See LICENSE for details.

## 👥 Contributing

Contributions are welcome! Please open issues or submit pull requests.
