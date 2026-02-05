#!/usr/bin/env python3
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

"""
Demonstration of MCP Authorization Feature

This script demonstrates how the authorization prompts work with the
Google Analytics MCP server. It shows the approval flow that MCP clients
should implement.
"""

import asyncio


async def demonstrate_authorization():
    """Demonstrates the authorization approval flow."""

    print("=" * 70)
    print("MCP Authorization Feature Demonstration")
    print("=" * 70)
    print()

    # Import server components
    import analytics_mcp.server  # noqa: F401
    from analytics_mcp.coordinator import mcp
    from analytics_mcp.authorization import (
        requires_approval,
        get_approval_prompt_for_tool,
    )

    # Step 1: Discover available prompts
    print("Step 1: Discovering Authorization Prompts")
    print("-" * 70)
    prompts = await mcp.list_prompts()
    print(f"Available approval prompts: {len(prompts)}")
    for prompt in prompts:
        print(f"  • {prompt.name}")
        print(f"    {prompt.description.split('.')[0]}")
    print()

    # Step 2: List available tools and identify sensitive ones
    print("Step 2: Identifying Sensitive Tools")
    print("-" * 70)
    tools = await mcp.list_tools()
    print(f"Total tools: {len(tools)}")
    print("\nSensitive tools requiring approval:")
    for tool in tools:
        if requires_approval(tool.name):
            prompt_name = get_approval_prompt_for_tool(tool.name)
            print(f"  • {tool.name} → uses '{prompt_name}'")
    print()

    # Step 3: Demonstrate approval prompt for data access
    print("Step 3: Example - Requesting Data Access Approval")
    print("-" * 70)
    print(
        "Scenario: User wants to run a report on property 'properties/123456789'"
    )
    print()

    result = await mcp.get_prompt(
        "approve_data_access",
        {
            "operation": "run_report",
            "property_id": "properties/123456789",
            "data_scope": "pageview and event data for the last 30 days",
        },
    )

    approval_message = result.messages[0].content.text
    print("Approval Prompt Shown to User:")
    print("┌" + "─" * 68 + "┐")
    for line in approval_message.split("\n"):
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘")
    print()
    print("[User would see buttons: ✓ Approve  ✗ Deny]")
    print()

    # Step 4: Demonstrate approval prompt for account access
    print("Step 4: Example - Requesting Account Access Approval")
    print("-" * 70)
    print("Scenario: User wants to view account summaries")
    print()

    result = await mcp.get_prompt(
        "approve_account_access",
        {"operation": "get_account_summaries", "account_id": ""},
    )

    approval_message = result.messages[0].content.text
    print("Approval Prompt Shown to User:")
    print("┌" + "─" * 68 + "┐")
    for line in approval_message.split("\n"):
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘")
    print()
    print("[User would see buttons: ✓ Approve  ✗ Deny]")
    print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("The authorization feature ensures that:")
    print("  1. Users are informed about data access requests")
    print("  2. Explicit consent is required before sensitive operations")
    print("  3. Different approval types for data vs. account access")
    print("  4. MCP clients can implement proper authorization workflows")
    print()
    print("For detailed documentation, see: docs/AUTHORIZATION.md")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demonstrate_authorization())
