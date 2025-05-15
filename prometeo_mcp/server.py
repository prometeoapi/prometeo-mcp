import os
from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import Field

from prometeo import Client
from prometeo.exceptions import PrometeoError
from prometeo.banking.exceptions import BankingClientError
from prometeo.curp import exceptions, Gender, State
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from mcp.server.fastmcp.exceptions import ToolError

from prometeo_mcp.background_validation import create_validation_task, get_validation_status, validation_tasks
from prometeo_mcp.utils import get_param_description

from httpx import Timeout


# Load .env file from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


# Create MCP server
mcp = FastMCP("PrometeoAPI MCP")

# Load your API key from the environment
PROMETEO_API_KEY = os.environ.get("PROMETEO_API_KEY")
PROMETEO_ENVIRONMENT = os.environ.get("PROMETEO_ENVIRONMENT", "sandbox")
if not PROMETEO_API_KEY:
    raise RuntimeError("PROMETEO_API_KEY environment variable is not set")
HTTPX_TIMEOUT = Timeout(90.0)


# Initialize Prometeo client
client = Client(api_key=PROMETEO_API_KEY, environment=PROMETEO_ENVIRONMENT, timeout=HTTPX_TIMEOUT)
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
    state: State,
    birthdate: str,
    name: str,
    first_surname: str,
    last_surname: str,
    gender: Gender
) -> dict:
    """Query a CURP using personal data"""
    try:
        parsed_birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        return await client.curp.reverse_query(
            state, parsed_birthdate, name, first_surname, last_surname, gender
        )
    except (KeyError, ValueError) as e:
        return {"error": f"Invalid input: {str(e)}"}
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}


@mcp.tool()
async def validate_account(
    account_number: Annotated[
        str,
        Field(
            description=get_param_description("account_number")
        ),
    ],
    country_code: Annotated[
        str,
        Field(
            description=get_param_description("country_code")
        ),
    ],
    bank_code: Annotated[
        Optional[str],
        Field(
            description=get_param_description("bank_code")
        ),
    ] = None,
    document_number: Annotated[
        Optional[str],
        Field(
            description=get_param_description("document_number")
        ),
    ] = None,
    document_type: Annotated[
        Optional[str],
        Field(
            description=get_param_description("document_type")
        ),
    ] = None,
    branch_code: Annotated[
        Optional[str],
        Field(
            description=get_param_description("branch_code")
        ),
    ] = None,
    account_type: Annotated[
        Optional[str],
        Field(
            description=get_param_description("account_type")
        ),
    ] = None,
):
    """Validate an account with Prometeo"""
    try:
        validation_id = create_validation_task(
            client,
            account_number=account_number,
            country_code=country_code,
            bank_code=bank_code,
            document_number=document_number,
            document_type=document_type,
            branch_code=branch_code,
            account_type=account_type,
        )
        return {
            "validation_id": validation_id,
            "status": "started",
            "message": "Validation is being processed in background",
        }
    except PrometeoError as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def get_validation_result(validation_id: str):
    """Check the status or result of an account validation"""
    return get_validation_status(validation_id)


@mcp.tool()
async def get_tasks():
    return validation_tasks


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
