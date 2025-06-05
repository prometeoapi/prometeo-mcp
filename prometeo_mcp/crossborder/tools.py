from prometeo_mcp.mcp_instance import mcp
from typing import Optional, Union
from prometeo_mcp.config import client

from prometeo.crossborder.models import (
    IntentDataRequest,
    RefundIntentInput,
    PayoutTransferInput,
    CustomerInput,
    WithdrawalAccountInput,
    TaxIdTypeMX,
    TaxIdTypeBR,
    TaxIdTypePE,
)


@mcp.tool()
async def crossborder_create_intent(
    destination_id: str,
    concept: str,
    currency: str,
    amount: float,
    customer: str,
    external_id: str,
):
    """Create a crossborder payin intent"""
    try:
        intent = await client.crossborder.create_intent(
            IntentDataRequest(
                destination_id=destination_id,
                concept=concept,
                currency=currency,
                amount=amount,
                customer=customer,
                external_id=external_id,
            )
        )
        return intent
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_create_payout(
    origin: str,
    description: str,
    currency: str,
    amount: float,
    external_id: str,
    customer: str,
):
    """Create a crossborder payout transfer"""
    try:
        payout = await client.crossborder.create_payout(
            PayoutTransferInput(
                origin=origin,
                description=description,
                currency=currency,
                amount=amount,
                external_id=external_id,
                customer=customer,
            )
        )
        return payout
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_intent(intent_id: str):
    """Get a crossborder payin intent"""
    try:
        intent = await client.crossborder.get_intent(intent_id)
        return intent
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_payout(payout_id: str):
    """Get a crossborder payout transfer"""
    try:
        payout = await client.crossborder.get_payout(payout_id)
        return payout
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_list_intents():
    """List all crossborder payin intents"""
    try:
        intents = await client.crossborder.list_intents()
        return intents
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_list_payouts():
    """List all crossborder payout transfers"""
    try:
        payouts = await client.crossborder.list_payouts()
        return payouts
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_refund_intent(intent_id: str, external_id: str, amount: float):
    """Refund a crossborder payin intent"""
    try:
        intent = await client.crossborder.refund_intent(
            RefundIntentInput(
                intent_id=intent_id,
                external_id=external_id,
                amount=amount,
            )
        )
        return intent
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_create_customer(
    name: str,
    tax_id_type: Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE],
    tax_id: str,
    external_id: str,
    withdrawal_account: Optional[WithdrawalAccountInput] = None,
):
    """Create a crossborder customer"""
    try:
        customer = await client.crossborder.create_customer(
            CustomerInput(
                name=name,
                tax_id_type=tax_id_type,
                tax_id=tax_id,
                external_id=external_id,
                withdrawal_account=withdrawal_account,
            )
        )
        return customer
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_customer(customer_id: str):
    """Get a crossborder customer"""
    try:
        customer = await client.crossborder.get_customer(customer_id)
        return customer
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_list_customers():
    """List all crossborder customers"""
    try:
        customers = await client.crossborder.list_customers()
        return customers
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_update_customer(
    customer_id: str,
    name: Optional[str] = None,
    tax_id_type: Optional[Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]] = None,
    tax_id: Optional[str] = None,
    external_id: Optional[str] = None,
):
    """Update a crossborder customer"""
    try:
        customer = await client.crossborder.update_customer(
            customer_id,
            CustomerInput(
                name=name,
                tax_id_type=tax_id_type,
                tax_id=tax_id,
                external_id=external_id,
            ),
        )
        return customer
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_add_withdrawal_account(
    customer_id: str, withdrawal_account: WithdrawalAccountInput
):
    """Add a withdrawal account to a crossborder customer"""
    try:
        customer = await client.crossborder.add_withdrawal_account(
            customer_id, withdrawal_account
        )
        return customer
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_select_withdrawal_account(
    customer_id: str, withdrawal_account_id: str
):
    """Select a withdrawal account for a crossborder customer"""
    try:
        customer = await client.crossborder.select_withdrawal_account(
            customer_id, withdrawal_account_id
        )
        return customer
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_accounts():
    """Get all withdrawal accounts for a crossborder customer"""
    try:
        accounts = await client.crossborder.get_accounts()
        return accounts
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_account(account_id: str):
    """Get a withdrawal account for a crossborder customer"""
    try:
        account = await client.crossborder.get_account(account_id)
        return account
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def crossborder_get_account_transactions(account_id: str):
    """Get all transactions for a withdrawal account"""
    try:
        transactions = await client.crossborder.get_account_transactions(account_id)
        return transactions
    except Exception as e:
        return {"status": "error", "message": str(e)}
