# OAuth User Authentication Setup Guide

This guide explains how to set up OAuth 2.0 user authentication for the Google Analytics MCP Server. This allows the server to authenticate using your personal Google account instead of Application Default Credentials (ADC) or service accounts.

## When to Use OAuth Authentication

Use OAuth authentication when you want to:
- Authenticate with your personal Google account
- Access Google Analytics properties associated with your account
- Avoid setting up service accounts or ADC
- Run the server with user-level permissions

## Prerequisites

1. Python 3.10 or higher installed
2. pipx installed ([Install pipx](https://pipx.pypa.io/stable/#install-pipx))
3. Access to a Google Analytics property
4. A Google Cloud project with the required APIs enabled

## Setup Instructions

### Step 1: Enable Required APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Enable these APIs:
   - [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
   - [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

### Step 2: Create OAuth 2.0 Credentials

1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - Choose **"External"** user type (or "Internal" if using Google Workspace)
   - Fill in the required app information
   - Add your email as a test user
   - Add the scope: `https://www.googleapis.com/auth/analytics.readonly`
4. Create OAuth client ID:
   - Application type: **"Desktop app"**
   - Name: "Analytics MCP Server" (or any name you prefer)
5. Click **"CREATE"**
6. Download the JSON file by clicking the download button
7. Save the file to a secure location (e.g., `~/oauth-client-secrets.json`)

**Important**: Keep this file secure! It contains sensitive credentials.

### Step 3: Configure Environment Variables

You need to set the `GOOGLE_OAUTH_CLIENT_SECRETS` environment variable to point to your OAuth client secrets file.

#### Option A: Set in Gemini/Claude Configuration

Edit your `~/.gemini/settings.json` or Claude Desktop configuration:

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "pipx",
      "args": [
        "run",
        "analytics-mcp"
      ],
      "env": {
        "GOOGLE_OAUTH_CLIENT_SECRETS": "/path/to/your/oauth-client-secrets.json"
      }
    }
  }
}
```

#### Option B: Set System-Wide (Optional)

Add to your `~/.bashrc`, `~/.zshrc`, or equivalent:

```bash
export GOOGLE_OAUTH_CLIENT_SECRETS="/path/to/your/oauth-client-secrets.json"
```

### Step 4: Install the MCP Server

```bash
pipx install analytics-mcp
```

Or if already installed:

```bash
pipx upgrade analytics-mcp
```

### Step 5: Test the Authentication

When you first run a command that requires authentication, the server will:

1. Open your default web browser
2. Ask you to sign in with your Google account
3. Request permission to access Google Analytics (read-only)
4. Save the authentication token to `~/.analytics-mcp/token.json`

Subsequent requests will use the saved token automatically.

## How It Works

### Authentication Flow

1. **First Run**: 
   - Server checks for existing token at `~/.analytics-mcp/token.json`
   - If not found, initiates OAuth flow in your browser
   - You authenticate and grant permissions
   - Token is saved for future use

2. **Subsequent Runs**:
   - Server loads token from `~/.analytics-mcp/token.json`
   - Uses saved credentials automatically
   - Refreshes token if expired

3. **Token Refresh**:
   - Tokens expire after a period
   - Server automatically refreshes using the refresh token
   - No re-authentication needed unless refresh token is invalid

### Environment Variables

- **`GOOGLE_OAUTH_CLIENT_SECRETS`** (required): Path to OAuth client secrets JSON file
- **`GOOGLE_OAUTH_TOKEN_FILE`** (optional): Custom path for token storage (defaults to `~/.analytics-mcp/token.json`)

## Troubleshooting

### "OAuth client secrets file must be provided" Error

**Cause**: The `GOOGLE_OAUTH_CLIENT_SECRETS` environment variable is not set.

**Solution**: Set the environment variable in your MCP client configuration as shown in Step 3.

### "Could not load token file" Warning

**Cause**: Token file is corrupted or invalid.

**Solution**: Delete the token file and re-authenticate:

```bash
rm ~/.analytics-mcp/token.json
```

The next time you use the server, it will prompt you to authenticate again.

### Browser Doesn't Open Automatically

**Cause**: Running in an environment without a display (e.g., SSH session).

**Solution**: The OAuth flow requires a local browser. Run the server from a machine with a display, or use Application Default Credentials (ADC) instead.

### "Access blocked: This app's request is invalid" Error

**Cause**: OAuth consent screen not properly configured or missing required scopes.

**Solution**: 
1. Return to the OAuth consent screen configuration
2. Ensure `https://www.googleapis.com/auth/analytics.readonly` is in the scopes
3. Add yourself as a test user if using External user type

### Permission Denied Errors

**Cause**: Your Google account doesn't have access to the requested Analytics property.

**Solution**: Ensure your Google account has at least Viewer permissions on the Google Analytics property you're trying to access.

## Security Best Practices

1. **Protect your OAuth client secrets file**:
   - Never commit it to version control
   - Store it in a secure location with restricted permissions
   - Use `chmod 600` on Unix systems

2. **Token Storage**:
   - Tokens are stored at `~/.analytics-mcp/token.json`
   - This file should have restricted permissions
   - Never share this file

3. **Revoke Access**:
   - To revoke access, visit [Google Account Permissions](https://myaccount.google.com/permissions)
   - Find "Analytics MCP Server" (or your chosen name)
   - Click "Remove Access"

4. **Regular Review**:
   - Periodically review which applications have access to your Google account
   - Remove any unused applications

## Switching Between Authentication Methods

The server supports two authentication methods:

1. **OAuth (User Authentication)**: Enabled when `GOOGLE_OAUTH_CLIENT_SECRETS` is set
2. **ADC (Application Default Credentials)**: Used when `GOOGLE_OAUTH_CLIENT_SECRETS` is NOT set

To switch from OAuth to ADC:
- Remove the `GOOGLE_OAUTH_CLIENT_SECRETS` environment variable from your configuration
- Set up ADC using the instructions in the main [README.md](../README.md#configure-credentials-)

To switch from ADC to OAuth:
- Follow the setup instructions in this guide

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Analytics API Scopes](https://developers.google.com/analytics/devguides/config/mgmt/v3/authorization#scopes)
- [Managing OAuth Clients](https://support.google.com/cloud/answer/15549257)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)

## Support

For issues or questions:
- Check the [main README](../README.md)
- Open an issue on [GitHub](https://github.com/googleanalytics/google-analytics-mcp/issues)
- Join the discussion on [Discord](https://discord.com/channels/971845904002871346/1398002598665257060)
