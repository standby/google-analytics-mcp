# Authorization Examples

This document provides examples of how the authorization prompts work with the Google Analytics MCP server.

## Overview

The Google Analytics MCP server implements authorization according to the [MCP Security Guidelines](https://modelcontextprotocol.io/docs/tutorials/security/authorization). Before executing sensitive operations, the server provides approval prompts that request user consent.

## Available Approval Prompts

### approve_data_access

Requests approval before accessing Google Analytics data.

**Arguments:**
- `operation` (required): The operation requesting data access
- `property_id` (optional): The Google Analytics property ID being accessed
- `data_scope` (optional): Description of what data will be accessed

**Example Usage:**

```json
{
  "method": "prompts/get",
  "params": {
    "name": "approve_data_access",
    "arguments": {
      "operation": "run_report",
      "property_id": "properties/123456789",
      "data_scope": "pageview and event data for the last 30 days"
    }
  }
}
```

**Example Response:**

```json
{
  "description": "Request user approval to access Google Analytics data",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "The operation 'run_report' is requesting access to pageview and event data for the last 30 days.\n\nProperty ID: properties/123456789\n\nDo you approve this data access?"
      }
    }
  ]
}
```

### approve_account_access

Requests approval before accessing Google Analytics account information.

**Arguments:**
- `operation` (required): The operation requesting account access
- `account_id` (optional): The account ID being accessed

**Example Usage:**

```json
{
  "method": "prompts/get",
  "params": {
    "name": "approve_account_access",
    "arguments": {
      "operation": "get_account_summaries",
      "account_id": "12345"
    }
  }
}
```

**Example Response:**

```json
{
  "description": "Request user approval to access Google Analytics account information",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "The operation 'get_account_summaries' is requesting access to your Google Analytics account information.\n\nAccount ID: 12345\n\nDo you approve this account access?"
      }
    }
  ]
}
```

## Workflow for MCP Clients

1. **List Available Prompts**
   ```json
   {
     "method": "prompts/list"
   }
   ```

2. **Request User Approval**
   
   Before calling a sensitive tool like `run_report`, the client should:
   
   a. Call the appropriate approval prompt with relevant arguments
   b. Display the returned message to the user
   c. Collect user's approval/denial response

3. **Execute Tool (if approved)**
   
   If the user approves, proceed with the tool call:
   ```json
   {
     "method": "tools/call",
     "params": {
       "name": "run_report",
       "arguments": {
         "property_id": "properties/123456789",
         ...
       }
     }
   }
   ```

## Sensitive Tools

The following tools require user approval before execution:

| Tool Name | Approval Prompt | Description |
|-----------|----------------|-------------|
| `run_report` | `approve_data_access` | Runs a Google Analytics report |
| `run_realtime_report` | `approve_data_access` | Runs a realtime report |
| `get_account_summaries` | `approve_account_access` | Retrieves account information |
| `get_property_details` | `approve_account_access` | Returns property details |
| `list_google_ads_links` | `approve_account_access` | Lists Google Ads links |
| `get_custom_dimensions_and_metrics` | `approve_data_access` | Retrieves custom dimensions/metrics |

## Implementation Notes

- The authorization prompts are implemented using MCP's prompt feature
- Clients must implement the authorization workflow to ensure user consent
- The server does not enforce authorization checks on tool execution; this is the responsibility of the MCP client
- For production deployments, clients should always request and verify user approval before executing sensitive operations

## Best Practices

1. **Always Request Approval**: For sensitive operations, always use the approval prompts before executing tools
2. **Clear Communication**: Provide clear information to users about what data will be accessed
3. **Audit Trail**: Keep logs of user approvals for audit purposes
4. **Graceful Denial**: Handle user denials gracefully and provide appropriate feedback
5. **Session Management**: Consider implementing session-based approval caching to avoid repetitive prompts for the same user session
