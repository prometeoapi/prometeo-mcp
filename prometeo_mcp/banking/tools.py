from datetime import datetime
from typing import Optional, Any
from prometeo_mcp.config import client
from prometeo.banking.exceptions import BankingClientError
from prometeo_mcp.mcp_instance import mcp

_active_sessions = {}
_interactive_fields = {}


@mcp.tool()
async def banking_login(
    provider: str,
    username: str,
    password: str,
    session_key: Optional[str] = None,
    answer: Optional[str] = None,
) -> dict:
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
            await session.finish_login(provider, username, password, answer)

        if session.get_status() == "interaction_required":
            _interactive_fields[session_key] = session._interactive_field
            return {
                "status": "interaction_required",
                "session_key": session_key,
                "context": "OTP required",
            }
        return {
            "status": "success",
            "message": f"Logged in as {username}",
            "session_key": session_key,
        }
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def banking_get_accounts(session_key: str) -> Any:
    """Get list of accounts for an active session."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        accounts = await client.banking.get_accounts(session_key)
        return accounts
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def banking_get_movements(
    session_key: str,
    account_number: str,
    currency_code: str,
    start_date: datetime,
    end_date: datetime,
) -> Any:
    """Get movements for an account in a date range."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        session = client.banking.get_session(session_key)
        accounts = await session.get_accounts()
        account = next((a for a in accounts if a.number == account_number), None)
        if not account:
            return {"status": "error", "message": "Account not found"}
        movements = await client.banking.get_movements(
            session_key, account_number, currency_code, start_date, end_date
        )
        return movements
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}
    except ValueError as e:
        return {"status": "error", "message": f"Invalid date format: {str(e)}"}


@mcp.tool()
async def banking_logout(session_key: str) -> dict | None:
    """Logout of the current session."""
    if not _active_sessions.get(session_key):
        return {"status": "error", "message": "Invalid or expired session_id"}
    try:
        await client.banking.logout(session_key)
        _active_sessions.pop(session_key)
    except BankingClientError as e:
        return {"status": "error", "message": str(e)}
