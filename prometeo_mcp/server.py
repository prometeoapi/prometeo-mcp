from prometeo_mcp.mcp_instance import mcp

import prometeo_mcp.openapi.resource  # noqa
import prometeo_mcp.account_validation.tools  # noqa
import prometeo_mcp.curp.tools  # noqa
import prometeo_mcp.banking.tools  # noqa
import prometeo_mcp.crossborder.tools  # noqa

if __name__ == "__main__":
    mcp.run()
