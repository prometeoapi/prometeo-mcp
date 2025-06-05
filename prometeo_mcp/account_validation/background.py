import asyncio
from datetime import datetime
from typing import Optional
from uuid import uuid4


validation_tasks = {}


def create_validation_task(
    client,
    account_number: str,
    country_code: str,
    bank_code: Optional[str],
    document_number: Optional[str],
    document_type: Optional[str],
    branch_code: Optional[str],
    account_type: Optional[str],
    beneficiary_name: Optional[str] = None,
) -> str:
    validation_id = str(uuid4())
    validation_tasks[validation_id] = {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "message": "Validation is still processing",
    }

    # Schedule the task in the current running event loop
    asyncio.create_task(
        _async_validation_wrapper(
            validation_id,
            client,
            account_number,
            country_code,
            bank_code,
            document_number,
            document_type,
            branch_code,
            account_type,
            beneficiary_name,
        )
    )

    return validation_id


async def _async_validation_wrapper(
    validation_id: str,
    client,
    account_number: str,
    country_code: str,
    bank_code: Optional[str],
    document_number: Optional[str],
    document_type: Optional[str],
    branch_code: Optional[str],
    account_type: Optional[str],
    beneficiary_name: Optional[str] = None,
):
    try:
        validate_fn = client.account_validation.validate
        kwargs = {
            "account_number": account_number,
            "country_code": country_code,
            "bank_code": bank_code,
            "document_number": document_number,
            "document_type": document_type,
            "branch_code": branch_code,
            "account_type": account_type,
            "beneficiary_name": beneficiary_name,
        }

        result = validate_fn(**kwargs)

        if asyncio.iscoroutine(result):
            result = await result

        validation_tasks[validation_id]["status"] = "done"
        validation_tasks[validation_id]["message"] = "Validation result available"
        validation_tasks[validation_id]["result"] = result

    except Exception as e:
        validation_tasks[validation_id]["status"] = "error"
        validation_tasks[validation_id]["message"] = str(e)


def get_validation_status(validation_id: str):
    return validation_tasks.get(
        validation_id, {"status": "unknown", "message": "Validation not found"}
    )
