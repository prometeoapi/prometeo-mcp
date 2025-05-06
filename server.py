import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from prometeo.curp import exceptions, Gender, State
from prometeo import Client
from typing import Optional, List

# Create MCP server
mcp = FastMCP("PrometeoAPI MCP")

# Load your API key from the environment
PROMETEO_API_KEY = os.environ.get("PROMETEO_API_KEY")
PROMETEO_ENVIRONMENT = os.environ.get("PROMETEO_ENVIRONMENT", "sandbox")
if not PROMETEO_API_KEY:
    raise RuntimeError("PROMETEO_API_KEY environment variable is not set")

# Initialize Prometeo client
client = Client(api_key=PROMETEO_API_KEY, environment=PROMETEO_ENVIRONMENT)

# Tool: CURP direct query
@mcp.tool()
def curp_query(curp: str) -> dict:
    """Query an existing CURP"""
    try:
        return client.curp.query(curp)
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}

# Tool: CURP reverse query
@mcp.tool()
def curp_reverse_query(
    state: str | State,
    birthdate: str,
    name: str,
    first_surname: str,
    last_surname: str,
    gender: str
) -> dict:
    """Query a CURP using personal data"""
    try:
        parsed_state = State[state.upper()]
        parsed_gender = Gender[gender.upper()]
        parsed_birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
        return client.curp.reverse_query(
            parsed_state, parsed_birthdate, name, first_surname, last_surname, parsed_gender
        )
    except (KeyError, ValueError) as e:
        return {"error": f"Invalid input: {str(e)}"}
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}

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

# Start the server
if __name__ == "__main__":
    mcp.run()
