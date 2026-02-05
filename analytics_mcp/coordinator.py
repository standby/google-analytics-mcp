# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module declaring the singleton MCP instance.

The singleton allows other modules to register their tools with the same MCP
server using `@mcp.tool` annotations, thereby 'coordinating' the bootstrapping
of the server.
"""

from mcp.server.fastmcp import FastMCP
from analytics_mcp.authorization import (
    create_approval_prompts,
    format_approval_message,
)

# Creates the singleton.
mcp = FastMCP("Google Analytics Server")


# Register authorization prompts for sensitive operations
@mcp.prompt(name="approve_data_access")
async def approval_prompt_data_access(
    operation: str,
    property_id: str = "",
    data_scope: str = "Google Analytics data",
):
    """Request user approval to access Google Analytics data.

    Args:
        operation: The operation requesting data access
        property_id: The Google Analytics property ID being accessed (optional)
        data_scope: Description of what data will be accessed (optional)
    """
    message = format_approval_message(
        "approve_data_access",
        {
            "operation": operation,
            "property_id": property_id,
            "data_scope": data_scope,
        },
    )

    return [{"role": "user", "content": {"type": "text", "text": message}}]


@mcp.prompt(name="approve_account_access")
async def approval_prompt_account_access(operation: str, account_id: str = ""):
    """Request user approval to access Google Analytics account information.

    Args:
        operation: The operation requesting account access
        account_id: The account ID being accessed (optional)
    """
    message = format_approval_message(
        "approve_account_access",
        {"operation": operation, "account_id": account_id},
    )

    return [{"role": "user", "content": {"type": "text", "text": message}}]
