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

"""Authorization and approval prompts for Google Analytics MCP server."""

from typing import Dict, List, Any


def create_approval_prompts() -> List[Dict[str, Any]]:
    """Creates a list of approval prompt templates for sensitive operations.
    
    Returns:
        A list of prompt templates that request user approval for
        sensitive operations like data access and account modifications.
    """
    return [
        {
            "name": "approve_data_access",
            "description": "Request user approval to access Google Analytics data",
            "arguments": [
                {
                    "name": "operation",
                    "description": "The operation requesting data access (e.g., 'run_report', 'get_account_summaries')",
                    "required": True
                },
                {
                    "name": "property_id",
                    "description": "The Google Analytics property ID being accessed",
                    "required": False
                },
                {
                    "name": "data_scope",
                    "description": "Description of what data will be accessed",
                    "required": False
                }
            ]
        },
        {
            "name": "approve_account_access",
            "description": "Request user approval to access Google Analytics account information",
            "arguments": [
                {
                    "name": "operation",
                    "description": "The operation requesting account access",
                    "required": True
                },
                {
                    "name": "account_id",
                    "description": "The account ID being accessed",
                    "required": False
                }
            ]
        }
    ]


def format_approval_message(
    prompt_name: str, 
    arguments: Dict[str, Any]
) -> str:
    """Formats an approval request message based on the prompt and arguments.
    
    Args:
        prompt_name: The name of the approval prompt
        arguments: The arguments for the approval request
        
    Returns:
        A formatted approval message string
    """
    if prompt_name == "approve_data_access":
        operation = arguments.get("operation", "unknown operation")
        property_id = arguments.get("property_id", "")
        data_scope = arguments.get("data_scope", "Google Analytics data")
        
        message = f"The operation '{operation}' is requesting access to {data_scope}."
        if property_id:
            message += f"\n\nProperty ID: {property_id}"
        message += "\n\nDo you approve this data access?"
        
        return message
        
    elif prompt_name == "approve_account_access":
        operation = arguments.get("operation", "unknown operation")
        account_id = arguments.get("account_id", "")
        
        message = f"The operation '{operation}' is requesting access to your Google Analytics account information."
        if account_id:
            message += f"\n\nAccount ID: {account_id}"
        message += "\n\nDo you approve this account access?"
        
        return message
    
    return "An operation is requesting approval. Do you approve?"


def requires_approval(tool_name: str) -> bool:
    """Determines if a tool requires user approval before execution.
    
    Args:
        tool_name: The name of the tool being called
        
    Returns:
        True if the tool requires approval, False otherwise
    """
    # Tools that access sensitive data or account information
    sensitive_tools = {
        "run_report",
        "run_realtime_report",
        "get_account_summaries",
        "get_property_details",
        "list_google_ads_links",
        "get_custom_dimensions_and_metrics"
    }
    
    return tool_name in sensitive_tools


def get_approval_prompt_for_tool(tool_name: str) -> str:
    """Gets the appropriate approval prompt name for a given tool.
    
    Args:
        tool_name: The name of the tool being called
        
    Returns:
        The name of the approval prompt to use
    """
    # Tools that primarily access account information
    account_tools = {
        "get_account_summaries",
        "get_property_details",
        "list_google_ads_links"
    }
    
    if tool_name in account_tools:
        return "approve_account_access"
    else:
        return "approve_data_access"
