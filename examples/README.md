# Examples

This directory contains example scripts demonstrating how to use the Google Analytics MCP Server.

## OAuth Authentication Example

The `oauth_authentication_example.py` script demonstrates how to use OAuth 2.0 user authentication to access Google Analytics data.

### Prerequisites

1. Create OAuth 2.0 credentials in Google Cloud Console (see [OAUTH_SETUP.md](../docs/OAUTH_SETUP.md))
2. Download the client secrets JSON file
3. Enable the Google Analytics Admin API and Data API

### Usage

```bash
# Set the environment variable
export GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/your/client_secrets.json

# Run the example
python examples/oauth_authentication_example.py
```

### What it does

1. Checks if OAuth is properly configured
2. Authenticates with Google (opens browser on first run)
3. Fetches your Google Analytics account summaries
4. Displays the accounts and properties you have access to
5. Saves the token for future use (in `~/.analytics-mcp/token.json`)

### Expected Output

```
======================================================================
Google Analytics MCP - OAuth Authentication Example
======================================================================

Authenticating with Google Analytics...
If this is your first time, a browser window will open for authentication.

✓ Authentication successful!

Found 1 account(s):

1. Account: My Analytics Account
   Resource Name: accounts/12345678
   Properties: 3
      1. My Website (properties/123456789)
      2. My App (properties/987654321)
      3. Test Property (properties/111222333)

======================================================================
OAuth authentication is working correctly!
======================================================================
```

## More Examples Coming Soon

Additional examples will be added to demonstrate:
- Running custom reports
- Accessing realtime data
- Working with custom dimensions and metrics
- Using the MCP server programmatically
