from typing import Annotated, Optional
from pydantic import Field
from prometeo_mcp.utils import get_param_description
from prometeo_mcp.config import client
from prometeo_mcp.account_validation.background import (
    create_validation_task,
    get_validation_status,
    validation_tasks,
)
from prometeo.exceptions import PrometeoError
from prometeo_mcp.mcp_instance import mcp


@mcp.tool()
async def validate_account(
    account_number: Annotated[
        str,
        Field(description=get_param_description("account_number")),
    ],
    country_code: Annotated[
        str,
        Field(description=get_param_description("country_code")),
    ],
    bank_code: Annotated[
        Optional[str],
        Field(description=get_param_description("bank_code")),
    ] = None,
    document_number: Annotated[
        Optional[str],
        Field(description=get_param_description("document_number")),
    ] = None,
    document_type: Annotated[
        Optional[str],
        Field(description=get_param_description("document_type")),
    ] = None,
    branch_code: Annotated[
        Optional[str],
        Field(description=get_param_description("branch_code")),
    ] = None,
    account_type: Annotated[
        Optional[str],
        Field(description=get_param_description("account_type")),
    ] = None,
    beneficiary_name: Annotated[
        Optional[str],
        Field(description="Name of the account holder"),
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
            beneficiary_name=beneficiary_name,
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
