import os
from datetime import datetime
from typing import Optional, List

from prometeo import Client
from prometeo.banking.exceptions import BankingClientError
from prometeo.curp import exceptions, Gender, State
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv


# Load .env file from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


# Create MCP server
mcp = FastMCP("PrometeoAPI MCP")

# Load your API key from the environment
PROMETEO_API_KEY = os.environ.get("PROMETEO_API_KEY")
PROMETEO_ENVIRONMENT = os.environ.get("PROMETEO_ENVIRONMENT", "sandbox")
if not PROMETEO_API_KEY:
    raise RuntimeError("PROMETEO_API_KEY environment variable is not set")

# Initialize Prometeo client
client = Client(api_key=PROMETEO_API_KEY, environment=PROMETEO_ENVIRONMENT)
_active_sessions = {}
_interactive_fields = {}

# Tool: CURP direct query
@mcp.tool()
async def curp_query(curp: str) -> dict:
    """Query an existing CURP"""
    try:
        return await client.curp.query(curp)
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}

# Tool: CURP reverse query
@mcp.tool()
async def curp_reverse_query(
    state: str | State,
    birthdate: str,
    name: str,
    first_surname: str,
    last_surname: str,
    gender: str
) -> dict:
    """Query a CURP using personal data"""
    try:
        parsed_state = State(state.upper())
        parsed_gender = Gender(gender.upper())
        parsed_birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        return await client.curp.reverse_query(
            parsed_state, parsed_birthdate, name, first_surname, last_surname, parsed_gender
        )
    except (KeyError, ValueError) as e:
        return {"error": f"Invalid input: {str(e)}"}
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}

# Tool: Validate Accounts
@mcp.tool()
async def validate_account(
    account_number: str,
    country_code: str,
    bank_code: Optional[str] = None,
    document_number: Optional[str] = None,
    branch_code: Optional[str] = None,
    account_type: Optional[List[str]] = None,
):
    """Validate an account with Prometeo"""
    return await client.account_validation.validate(
        account_number=account_number,
        country_code=country_code,
        bank_code=bank_code,
        document_number=document_number,
        branch_code=branch_code,
        account_type=account_type,
    )


@mcp.tool()
async def banking_login(provider: str, username: str, password: str, session_key: Optional[str] = None, answer: Optional[str] = None) -> dict:
    """Login to a banking provider and store session by session_id.
    If the session retrieves interaction_required, ask for OTP and retry login with provided session_key"""
    try:
        if session_key is None:
            session = client.banking.new_session()
            await session.login(provider=provider, username=username, password=password)
            session_key = session._session_key
            _active_sessions[session_key] = True
        else:
            session = client.banking.get_session(session_key)
            session._interactive_field = _interactive_fields[session_key]
            await session.finish_login(
                provider,
                username,
                password,
                answer
            )

        if session.get_status() == 'interaction_required':
            _interactive_fields[session_key] = session._interactive_field
            return {"status": "interaction_required", "session_key": session_key, "context": "OTP required"}
        return {"status": "success", "message": f"Logged in as {username}", "session_key": session_key}
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def banking_get_accounts(session_key: str) -> dict:
    """Get list of accounts for an active session."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        accounts = await client.banking.get_accounts(session_key)
        return accounts
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def banking_get_movements(session_key: str, account_number: str, currency_code: str, start_date: datetime, end_date: datetime) -> dict:
    """Get movements for an account in a date range."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        session = client.banking.get_session(session_key)
        accounts = await session.get_accounts()
        account = next((a for a in accounts if a.number == account_number), None)
        if not account:
            return {"status": "error", "message": "Account not found"}
        movements = await client.banking.get_movements(session_key, account_number, currency_code, start_date, end_date)
        return movements
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "error", "message": f"Invalid date format: {str(e)}"}

@mcp.tool()
async def banking_logout(session_key: str) -> dict:
    """Logout of the current session."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        await client.banking.logout(session_key)
        _active_sessions.pop(session_key)
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}


# Start the server
if __name__ == "__main__":
    mcp.run()
