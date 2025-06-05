import os
import mcp.types as types
from prometeo_mcp.config import OPENAPI_PATH
from prometeo_mcp.server import mcp


@mcp.resource("openapi://all")
async def list_openapi_resources() -> list[types.Resource]:
    return [
        types.Resource(uri=f"openapi://{i}", name=i, mimeType="application/yaml")
        for i in os.listdir(OPENAPI_PATH)
        if i.endswith(".yml")
    ]


@mcp.resource("openapi://{document_id}")
async def read_openapi_resource(document_id: str) -> str:
    with open(f"{OPENAPI_PATH}/{document_id}", "r") as f:
        return f.read()
    raise ValueError("Resource not found")
