import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from prometeo_mcp.background_validation import validation_tasks
from prometeo_mcp.server import (
    curp_query,
    curp_reverse_query,
    validate_account,
    validate_account,
    banking_login,
    banking_get_accounts,
    banking_get_movements,
    banking_logout,
    _active_sessions,
    _interactive_fields
)

# Replace 'prometeo_mcp.server' with the actual module name

@pytest.mark.asyncio
async def test_curp_query_success():
    with patch("prometeo_mcp.server.client.curp.query", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = {"curp": "ABC123"}
        result = await curp_query("ABC123")
        assert result == {"curp": "ABC123"}
        mock_query.assert_awaited_once_with("ABC123")


@pytest.mark.asyncio
async def test_curp_query_error():
    mock_error = Exception("Invalid CURP")
    with patch("prometeo_mcp.server.client.curp.query", new_callable=AsyncMock, side_effect=mock_error):
        with pytest.raises(Exception) as exc_info:
            await curp_query("INVALID")
        assert "Invalid CURP" in str(exc_info.value)


@pytest.mark.asyncio
async def test_curp_reverse_query_success():
    with patch("prometeo_mcp.server.client.curp.reverse_query", new_callable=AsyncMock) as mock_reverse:
        mock_reverse.return_value = {"curp": "XYZ789"}
        result = await curp_reverse_query(
            state="OC",
            birthdate="2000-01-01",
            name="JUAN",
            first_surname="PEREZ",
            last_surname="LOPEZ",
            gender="H"
        )
        assert result == {"curp": "XYZ789"}


@pytest.mark.asyncio
async def test_curp_reverse_query_invalid_input():
    result = await curp_reverse_query(
        state="INVALID",
        birthdate="wrong-date",
        name="JOHN",
        first_surname="DOE",
        last_surname="SMITH",
        gender="UNKNOWN"
    )
    assert isinstance(result, dict)
    assert "error" in result



@pytest.mark.asyncio
async def test_validate_account_success():
    with patch("prometeo_mcp.server.client.account_validation.validate", new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = {"valid": True}
        result = await validate_account(
            account_number="12345678",
            country_code="MX",
            bank_code=None,
            document_number=None,
            document_type=None,
            branch_code=None,
            account_type=None,
        )
        validation_id = result["validation_id"]
        assert result["status"] == 'started'
        await asyncio.sleep(0.1)

        stored = validation_tasks[validation_id]
        assert stored["status"] == "done"
        assert stored["result"] == {"valid": True}


@pytest.mark.asyncio
async def test_banking_login_new_session_success():
    session_mock = MagicMock()
    session_mock.login = AsyncMock()
    session_mock.get_status.return_value = "success"
    session_mock._session_key = "sess123"

    with patch("prometeo_mcp.server.client.banking.new_session", return_value=session_mock):
        result = await banking_login("bbva", "user", "pass")
        assert result["status"] == "success"
        assert result["session_key"] == "sess123"


@pytest.mark.asyncio
async def test_banking_get_accounts_invalid_session():
    result = await banking_get_accounts("invalid_key")
    assert result["status"] == "error"
    assert "Invalid or expired" in result["message"]


@pytest.mark.asyncio
async def test_banking_get_movements_account_not_found():
    _active_sessions["valid_key"] = True
    session_mock = MagicMock()
    session_mock.get_accounts = AsyncMock(return_value=[])
    with patch("prometeo_mcp.server.client.banking.get_session", return_value=session_mock), \
         patch("prometeo_mcp.server.client.banking.get_movements", new=AsyncMock()):
        result = await banking_get_movements("valid_key", "1234", "MXN", datetime.now(), datetime.now())
        assert result["status"] == "error"
        assert result["message"] == "Account not found"


@pytest.mark.asyncio
async def test_banking_logout_success():
    _active_sessions["logout_key"] = True
    with patch("prometeo_mcp.server.client.banking.logout", new=AsyncMock(return_value=None)) as mock_logout:
        result = await banking_logout("logout_key")
        assert result is None or result == {}
        mock_logout.assert_called_once_with("logout_key")


@pytest.mark.asyncio
async def test_banking_logout_invalid_session():
    result = await banking_logout("missing_key")
    assert result["status"] == "error"
    assert "Invalid or expired" in result["message"]
