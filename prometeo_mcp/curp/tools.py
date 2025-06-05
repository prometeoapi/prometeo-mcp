from datetime import datetime
from prometeo.curp.models import QueryResult
from prometeo.curp import exceptions, Gender, State
from prometeo_mcp.config import client
from prometeo_mcp.mcp_instance import mcp


@mcp.tool()
async def curp_query(curp: str) -> QueryResult | dict:
    """Query an existing CURP"""
    try:
        return await client.curp.query(curp)
    except exceptions.CurpError as e:
        return {"error": f"CURP does not exist: {e.message}"}


@mcp.tool()
async def curp_reverse_query(
    state: State,
    birthdate: str,
    name: str,
    first_surname: str,
    last_surname: str,
    gender: Gender,
) -> QueryResult | dict:
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
