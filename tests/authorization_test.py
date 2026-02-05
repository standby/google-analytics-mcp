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

"""Tests for the authorization module."""

import unittest
from analytics_mcp.authorization import (
    create_approval_prompts,
    format_approval_message,
    requires_approval,
    get_approval_prompt_for_tool
)


class TestAuthorization(unittest.TestCase):
    """Test cases for authorization functionality."""

    def test_create_approval_prompts(self):
        """Test that approval prompts are created correctly."""
        prompts = create_approval_prompts()
        
        self.assertIsInstance(prompts, list)
        self.assertGreater(len(prompts), 0)
        
        # Check that required prompts exist
        prompt_names = [p['name'] for p in prompts]
        self.assertIn('approve_data_access', prompt_names)
        self.assertIn('approve_account_access', prompt_names)
        
        # Verify prompt structure
        for prompt in prompts:
            self.assertIn('name', prompt)
            self.assertIn('description', prompt)
            self.assertIn('arguments', prompt)
            self.assertIsInstance(prompt['arguments'], list)

    def test_format_approval_message_data_access(self):
        """Test formatting of data access approval message."""
        message = format_approval_message(
            "approve_data_access",
            {
                "operation": "run_report",
                "property_id": "properties/123456",
                "data_scope": "pageview data"
            }
        )
        
        self.assertIn("run_report", message)
        self.assertIn("properties/123456", message)
        self.assertIn("pageview data", message)
        self.assertIn("approve", message.lower())

    def test_format_approval_message_account_access(self):
        """Test formatting of account access approval message."""
        message = format_approval_message(
            "approve_account_access",
            {
                "operation": "get_account_summaries",
                "account_id": "12345"
            }
        )
        
        self.assertIn("get_account_summaries", message)
        self.assertIn("12345", message)
        self.assertIn("approve", message.lower())

    def test_format_approval_message_minimal(self):
        """Test formatting with minimal arguments."""
        message = format_approval_message(
            "approve_data_access",
            {
                "operation": "test_operation"
            }
        )
        
        self.assertIn("test_operation", message)
        self.assertIn("approve", message.lower())

    def test_requires_approval_sensitive_tools(self):
        """Test that sensitive tools require approval."""
        sensitive_tools = [
            "run_report",
            "run_realtime_report",
            "get_account_summaries",
            "get_property_details",
            "list_google_ads_links",
            "get_custom_dimensions_and_metrics"
        ]
        
        for tool in sensitive_tools:
            self.assertTrue(
                requires_approval(tool),
                f"Tool '{tool}' should require approval"
            )

    def test_requires_approval_non_sensitive(self):
        """Test that non-existent tools don't require approval."""
        self.assertFalse(requires_approval("non_existent_tool"))
        self.assertFalse(requires_approval("random_operation"))

    def test_get_approval_prompt_for_tool_account(self):
        """Test getting approval prompt for account-related tools."""
        account_tools = [
            "get_account_summaries",
            "get_property_details",
            "list_google_ads_links"
        ]
        
        for tool in account_tools:
            prompt = get_approval_prompt_for_tool(tool)
            self.assertEqual(prompt, "approve_account_access")

    def test_get_approval_prompt_for_tool_data(self):
        """Test getting approval prompt for data-related tools."""
        data_tools = [
            "run_report",
            "run_realtime_report",
            "get_custom_dimensions_and_metrics"
        ]
        
        for tool in data_tools:
            prompt = get_approval_prompt_for_tool(tool)
            self.assertEqual(prompt, "approve_data_access")


if __name__ == '__main__':
    unittest.main()
