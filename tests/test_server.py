import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from prometeo_mcp.account_validation.background import validation_tasks
from prometeo_mcp.curp.tools import curp_query, curp_reverse_query
from prometeo_mcp.account_validation.tools import validate_account
from prometeo_mcp.banking.tools import (
    banking_login,
    banking_get_accounts,
    banking_get_movements,
    banking_logout,
    _active_sessions,
)
from prometeo_mcp.crossborder.tools import (
    crossborder_create_customer,
    crossborder_create_intent,
    crossborder_create_payout,
    crossborder_refund_intent,
    crossborder_get_customer,
    crossborder_add_withdrawal_account,
    crossborder_get_account,
    crossborder_get_accounts,
    crossborder_get_account_transactions,
)
from prometeo.crossborder.models import (
    WithdrawalAccountInput,
    CustomerInput,
    RefundIntentInput,
    PayoutTransferInput,
    IntentDataRequest,
)


@pytest.mark.asyncio
async def test_curp_query_success():
    with patch(
        "prometeo_mcp.curp.tools.client.curp.query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.return_value = {"curp": "ABC123"}
        result = await curp_query("ABC123")
        assert result == {"curp": "ABC123"}
        mock_query.assert_awaited_once_with("ABC123")


@pytest.mark.asyncio
async def test_curp_query_error():
    mock_error = Exception("Invalid CURP")
    with patch(
        "prometeo_mcp.curp.tools.client.curp.query",
        new_callable=AsyncMock,
        side_effect=mock_error,
    ):
        with pytest.raises(Exception) as exc_info:
            await curp_query("INVALID")
        assert "Invalid CURP" in str(exc_info.value)


@pytest.mark.asyncio
async def test_curp_reverse_query_success():
    with patch(
        "prometeo_mcp.curp.tools.client.curp.reverse_query", new_callable=AsyncMock
    ) as mock_reverse:
        mock_reverse.return_value = {"curp": "XYZ789"}
        result = await curp_reverse_query(
            state="OC",
            birthdate="2000-01-01",
            name="JUAN",
            first_surname="PEREZ",
            last_surname="LOPEZ",
            gender="H",
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
        gender="UNKNOWN",
    )
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
async def test_validate_account_success():
    with patch(
        "prometeo_mcp.account_validation.tools.client.account_validation.validate",
        new_callable=AsyncMock,
    ) as mock_validate:
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
        assert result["status"] == "started"
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

    with patch(
        "prometeo_mcp.banking.tools.client.banking.new_session",
        return_value=session_mock,
    ):
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
    with patch(
        "prometeo_mcp.banking.tools.client.banking.get_session",
        return_value=session_mock,
    ), patch(
        "prometeo_mcp.banking.tools.client.banking.get_movements", new=AsyncMock()
    ):
        result = await banking_get_movements(
            "valid_key", "1234", "MXN", datetime.now(), datetime.now()
        )
        assert result["status"] == "error"
        assert result["message"] == "Account not found"


@pytest.mark.asyncio
async def test_banking_logout_success():
    _active_sessions["logout_key"] = True
    with patch(
        "prometeo_mcp.banking.tools.client.banking.logout",
        new=AsyncMock(return_value=None),
    ) as mock_logout:
        result = await banking_logout("logout_key")
        assert result is None or result == {}
        mock_logout.assert_called_once_with("logout_key")


@pytest.mark.asyncio
async def test_banking_logout_invalid_session():
    result = await banking_logout("missing_key")
    assert result["status"] == "error"
    assert "Invalid or expired" in result["message"]


@pytest.mark.asyncio
async def test_crossborder_create_customer_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.create_customer",
        new_callable=AsyncMock,
    ) as mock_create_customer:
        mock_create_customer.return_value = {"customer": "customer_id"}
        result = await crossborder_create_customer(
            name="John Doe",
            tax_id_type="rfc",
            tax_id="ABCD1234",
            external_id="external_id",
            withdrawal_account=WithdrawalAccountInput(
                account_format="clabe",
                account_number="1234567890",
                bicfi="BCMRMXMM",
                selected=True,
            ),
        )
        assert result == {"customer": "customer_id"}
        mock_create_customer.assert_awaited_once_with(
            CustomerInput(
                name="John Doe",
                tax_id_type="rfc",
                tax_id="ABCD1234",
                external_id="external_id",
                withdrawal_account=WithdrawalAccountInput(
                    account_format="clabe",
                    account_number="1234567890",
                    bicfi="BCMRMXMM",
                    selected=True,
                ),
            )
        )


@pytest.mark.asyncio
async def test_crossborder_create_customer_invalid_input():
    result = await crossborder_create_customer(
        name="John Doe",
        tax_id_type="invalid",
        tax_id="ABCD1234",
        external_id="external_id",
        withdrawal_account=WithdrawalAccountInput(
            account_format="clabe",
            account_number="1234567890",
            bicfi="BCMRMXMM",
            selected=True,
        ),
    )
    assert isinstance(result, dict)
    assert "Input should be 'cnpj'" in result["message"]


@pytest.mark.asyncio
async def test_crossborder_create_payin_intent_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.create_intent",
        new_callable=AsyncMock,
    ) as mock_create_intent:
        mock_create_intent.return_value = {"intent": "intent_id"}
        result = await crossborder_create_intent(
            destination_id="destination_id",
            concept="concept",
            currency="MXN",
            amount=100,
            customer="customer_id",
            external_id="external_id",
        )
        assert result == {"intent": "intent_id"}
        mock_create_intent.assert_awaited_once_with(
            IntentDataRequest(
                destination_id="destination_id",
                concept="concept",
                currency="MXN",
                amount=100,
                customer="customer_id",
                external_id="external_id",
            )
        )


@pytest.mark.asyncio
async def test_crossborder_create_payin_intent_invalid_input():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.create_intent",
        new_callable=AsyncMock,
    ) as mock_create_intent:
        mock_create_intent.side_effect = Exception("Error")
        result = await crossborder_create_intent(
            destination_id="destination_id",
            concept="concept",
            currency="MXN",
            amount=100,
            customer="customer_id",
            external_id="external_id",
        )
        assert isinstance(result, dict)
        assert result["status"] == "error"


@pytest.mark.asyncio
async def test_crossborder_create_payout_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.create_payout",
        new_callable=AsyncMock,
    ) as mock_create_payout:
        mock_create_payout.return_value = {"payout": "payout_id"}
        result = await crossborder_create_payout(
            origin="origin",
            description="description",
            currency="MXN",
            amount=100,
            external_id="external_id",
            customer="customer_id",
        )
        assert result == {"payout": "payout_id"}
        mock_create_payout.assert_awaited_once_with(
            PayoutTransferInput(
                origin="origin",
                description="description",
                currency="MXN",
                amount=100,
                external_id="external_id",
                customer="customer_id",
            )
        )


@pytest.mark.asyncio
async def test_crossborder_create_payout_invalid_input():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.create_payout",
        new_callable=AsyncMock,
    ) as mock_create_payout:
        mock_create_payout.side_effect = Exception("Error")
        result = await crossborder_create_payout(
            origin="origin",
            description="description",
            currency="MXN",
            amount=100,
            external_id="external_id",
            customer="customer_id",
        )
        assert isinstance(result, dict)
        assert result["status"] == "error"


@pytest.mark.asyncio
async def test_crossborder_refund_intent_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.refund_intent",
        new_callable=AsyncMock,
    ) as mock_refund_intent:
        mock_refund_intent.return_value = {"intent": "intent_id"}
        result = await crossborder_refund_intent(
            intent_id="intent_id",
            external_id="external_id",
            amount=100,
        )
        assert result == {"intent": "intent_id"}
        mock_refund_intent.assert_awaited_once_with(
            RefundIntentInput(
                intent_id="intent_id",
                external_id="external_id",
                amount=100,
            )
        )


@pytest.mark.asyncio
async def test_crossborder_refund_intent_invalid_input():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.refund_intent",
        new_callable=AsyncMock,
    ) as mock_refund_intent:
        mock_refund_intent.side_effect = Exception("Error")
        result = await crossborder_refund_intent(
            intent_id="intent_id",
            external_id="external_id",
            amount=100,
        )
        assert isinstance(result, dict)
        assert result["status"] == "error"


@pytest.mark.asyncio
async def test_crossborder_get_customer_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.get_customer",
        new_callable=AsyncMock,
    ) as mock_get_customer:
        mock_get_customer.return_value = {"customer": "customer_id"}
        result = await crossborder_get_customer("customer_id")
        assert result == {"customer": "customer_id"}
        mock_get_customer.assert_awaited_once_with("customer_id")


@pytest.mark.asyncio
async def test_crossborder_add_withdrawal_account_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.add_withdrawal_account",
        new_callable=AsyncMock,
    ) as mock_add_withdrawal_account:
        mock_add_withdrawal_account.return_value = {"customer": "customer_id"}
        result = await crossborder_add_withdrawal_account(
            customer_id="customer_id",
            withdrawal_account=WithdrawalAccountInput(
                account_format="clabe",
                account_number="1234567890",
                bicfi="BCMRMXMM",
                selected=True,
            ),
        )
        assert result == {"customer": "customer_id"}
        mock_add_withdrawal_account.assert_awaited_once_with(
            "customer_id",
            WithdrawalAccountInput(
                account_format="clabe",
                account_number="1234567890",
                bicfi="BCMRMXMM",
                selected=True,
            ),
        )


@pytest.mark.asyncio
async def test_crossborder_add_withdrawal_account_invalid_input():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.add_withdrawal_account",
        new_callable=AsyncMock,
    ) as mock_add_withdrawal_account:
        mock_add_withdrawal_account.side_effect = Exception("Error")
        result = await crossborder_add_withdrawal_account(
            customer_id="customer_id",
            withdrawal_account=WithdrawalAccountInput(
                account_format="clabe",
                account_number="1234567890",
                bicfi="BCMRMXMM",
                selected=True,
            ),
        )
        assert isinstance(result, dict)
        assert result["status"] == "error"


@pytest.mark.asyncio
async def test_crossborder_get_account_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.get_account",
        new_callable=AsyncMock,
    ) as mock_get_account:
        mock_get_account.return_value = {"account": "account_id"}
        result = await crossborder_get_account("account_id")
        assert result == {"account": "account_id"}
        mock_get_account.assert_awaited_once_with("account_id")


@pytest.mark.asyncio
async def test_crossborder_get_accounts_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.get_accounts",
        new_callable=AsyncMock,
    ) as mock_get_accounts:
        mock_get_accounts.return_value = {"accounts": "accounts_id"}
        result = await crossborder_get_accounts()
        assert result == {"accounts": "accounts_id"}
        mock_get_accounts.assert_awaited_once()


@pytest.mark.asyncio
async def test_crossborder_get_account_transactions_success():
    with patch(
        "prometeo_mcp.crossborder.tools.client.crossborder.get_account_transactions",
        new_callable=AsyncMock,
    ) as mock_get_movements:
        mock_get_movements.return_value = {"movements": "movements_id"}
        result = await crossborder_get_account_transactions("account_id")
        assert result == {"movements": "movements_id"}
        mock_get_movements.assert_awaited_once_with("account_id")
