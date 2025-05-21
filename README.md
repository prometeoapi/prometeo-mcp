# Prometeo MCP Server

A server implementation for MCP (Model Context Protocol) to connect Prometeo API. Include functions to access banking information, validate accounts and query CURP.

---

## 🚀 Features

- ✅ Python 3.11+
- ✅ Pydantic v2.x
- ✅ FastMCP integration
- ✅ Prometeo API SDK

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

This project supports MCP (Model Context Protocol) integration and can be configured for execution inside LLM tools or agents that support external server launching.

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
    func=lambda x: os.system("uv run prometeo_mcp/server.py"),
    description="Runs Prometeo API server"
)
```

---

##  🛠 Tools

### CURP Query Tools

#### `curp_query`

Allows you to validate and retrieve information associated with an existing CURP (Clave Única de Registro de Población) by providing the CURP code directly. This function is essential for verifying Mexican identity documents and obtaining associated personal data.

#### `curp_reverse_query`

Enables retrieval of a CURP by providing personal demographic data instead of the CURP itself. This function requires name, surnames, gender, birthdate, and state of registration to find the corresponding CURP.

### Account Validation Tools

#### `validate_account`

Validates bank account information across multiple Latin American countries (Argentina, Brazil, Colombia, Chile, Ecuador, Mexico, Peru, Uruguay) and the United States. This function verifies if an account exists and returns details about the account holder. It handles various account number formats including CLABE (Mexico), CBU/CVU (Argentina), CCI (Peru), and PIX keys (Brazil).

#### `get_validation_result`

Retrieves the status or result of a previously initiated account validation request. This is particularly useful for asynchronous validations that may take time to process through banking systems.


#### `get_tasks`

Retrieves information about system tasks and their statuses. This function is useful for monitoring background processes and understanding the overall system state.

### Banking Connection Tools

#### `banking_login`
Establishes a connection with a banking provider by authenticating user credentials. It handles multi-factor authentication scenarios by returning a session key that can be used for subsequent operations. If two-factor authentication is required, the function signals that an OTP (One-Time Password) is needed.

#### `banking_get_accounts`

Retrieves a list of all accounts associated with an authenticated banking session. This provides account numbers, types, balances, and other relevant details once a user is successfully logged in.

#### `banking_get_movements`

Obtains transaction history (movements) for a specific account within a defined date range. This function requires an active session key, account number, currency code, and the desired date range for the transactions.

#### `banking_logout`

Securely terminates an active banking session, ensuring proper cleanup of authentication tokens and session data.

##  OpenAPI Resources

### `openapi://all`

Lists all available OpenAPI resources. From this list you can select a resource to read.

### `openapi://{document_id}`

Reads a specific OpenAPI resource by its ID. From this resource you can generate client code to interact with the any Prometeo API.

---

### 💡 Prompt Examples

To see how to interact with this MCP server via supported LLMs, check out:

📁 [`examples/prompts.md`](examples/prompts.md)

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
