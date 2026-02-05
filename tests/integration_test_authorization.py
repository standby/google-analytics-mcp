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

"""Integration test for authorization flow."""

import asyncio
import sys


async def test_authorization_integration():
    """Test the complete authorization integration."""

    print("Testing MCP Authorization Integration\n")
    print("=" * 60)

    try:
        # Import the server to ensure all tools are registered
        import analytics_mcp.server  # noqa: F401
        from analytics_mcp.coordinator import mcp
        from analytics_mcp.authorization import (
            requires_approval,
            get_approval_prompt_for_tool,
        )

        # Test 1: Verify prompts are registered
        print("\n1. Checking registered prompts...")
        prompts = await mcp.list_prompts()
        assert len(prompts) == 2, f"Expected 2 prompts, got {len(prompts)}"
        prompt_names = [p.name for p in prompts]
        assert "approve_data_access" in prompt_names
        assert "approve_account_access" in prompt_names
        print("   ✓ Authorization prompts registered correctly")

        # Test 2: Verify tools are registered
        print("\n2. Checking registered tools...")
        tools = await mcp.list_tools()
        assert len(tools) > 0, "No tools registered"
        print(f"   ✓ {len(tools)} tools registered")

        # Test 3: Test approval prompt for data access
        print("\n3. Testing data access approval prompt...")
        result = await mcp.get_prompt(
            "approve_data_access",
            {
                "operation": "run_report",
                "property_id": "properties/123456789",
                "data_scope": "pageview data",
            },
        )
        assert result is not None
        assert hasattr(result, "messages")
        assert len(result.messages) > 0
        message_text = result.messages[0].content.text
        assert "run_report" in message_text
        assert "pageview data" in message_text
        assert "approve" in message_text.lower()
        print("   ✓ Data access prompt works correctly")

        # Test 4: Test approval prompt for account access
        print("\n4. Testing account access approval prompt...")
        result = await mcp.get_prompt(
            "approve_account_access",
            {"operation": "get_account_summaries", "account_id": "12345"},
        )
        assert result is not None
        assert hasattr(result, "messages")
        message_text = result.messages[0].content.text
        assert "get_account_summaries" in message_text
        assert "12345" in message_text
        print("   ✓ Account access prompt works correctly")

        # Test 5: Verify sensitive tools mapping
        print("\n5. Checking sensitive tool classification...")
        sensitive_count = 0
        for tool in tools:
            if requires_approval(tool.name):
                prompt_name = get_approval_prompt_for_tool(tool.name)
                assert prompt_name in [
                    "approve_data_access",
                    "approve_account_access",
                ]
                sensitive_count += 1
        assert sensitive_count > 0, "No sensitive tools identified"
        print(f"   ✓ {sensitive_count} sensitive tools correctly classified")

        # Test 6: Verify prompt arguments
        print("\n6. Checking prompt arguments...")
        for prompt in prompts:
            assert (
                len(prompt.arguments) > 0
            ), f"Prompt {prompt.name} has no arguments"
            # All prompts should have 'operation' argument
            arg_names = [arg.name for arg in prompt.arguments]
            assert (
                "operation" in arg_names
            ), f"Prompt {prompt.name} missing 'operation' argument"
        print("   ✓ All prompts have required arguments")

        print("\n" + "=" * 60)
        print("✅ All authorization integration tests passed!")
        print("\nSummary:")
        print(f"  - {len(prompts)} authorization prompts")
        print(f"  - {len(tools)} total tools")
        print(f"  - {sensitive_count} sensitive tools requiring approval")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_authorization_integration())
    sys.exit(exit_code)
