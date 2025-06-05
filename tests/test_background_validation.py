import pytest
import asyncio
from prometeo_mcp.account_validation.background import (
    create_validation_task,
    get_validation_status,
    validation_tasks,
)
from prometeo.exceptions import PrometeoError


class DummyClient:
    class DummyValidation:
        async def validate(self, **kwargs):
            return {"validated": True, "account": kwargs["account_number"]}

    def __init__(self, should_fail=False):
        self.account_validation = self.DummyValidation()
        if should_fail:
            self.account_validation.validate = self._fail

    async def _fail(self, **kwargs):
        raise PrometeoError("Validation failed")


@pytest.mark.asyncio
async def test_create_validation_task_success():
    client = DummyClient()
    task_id = create_validation_task(
        client,
        account_number="123",
        country_code="CL",
        bank_code="0012",
        document_number="99999999-9",
        document_type="RUT",
        branch_code=None,
        account_type="CHECKING",
    )

    assert task_id in validation_tasks
    assert validation_tasks[task_id]["status"] == "pending"
    assert "created_at" in validation_tasks[task_id]

    # Wait for background task to complete
    await asyncio.sleep(0.1)

    result = get_validation_status(task_id)
    assert result["status"] == "done"
    assert result["result"]["validated"] is True


@pytest.mark.asyncio
async def test_create_validation_task_failure():
    client = DummyClient(should_fail=True)
    task_id = create_validation_task(
        client,
        account_number="123",
        country_code="CL",
        bank_code="0012",
        document_number="99999999-9",
        document_type="RUT",
        branch_code=None,
        account_type="CHECKING",
    )

    assert task_id in validation_tasks
    assert validation_tasks[task_id]["status"] == "pending"

    await asyncio.sleep(0.1)

    result = get_validation_status(task_id)
    assert result["status"] == "error"
    assert "Validation failed" in result["message"]


def test_get_unknown_validation_id():
    result = get_validation_status("non-existent-id")
    assert "Validation not found" in result["message"]
    assert result["status"] == "unknown"
