# Google Analytics MCP Server - Cloudflare Workers Setup Guide

This guide walks you through setting up the Google Analytics MCP Server on Cloudflare Workers.

## Prerequisites

Before you begin, ensure you have:

1. A [Cloudflare account](https://dash.cloudflare.com/sign-up)
2. [Node.js](https://nodejs.org/) (v18 or later) installed
3. A Google Cloud project with:
   - Google Analytics Admin API enabled
   - Google Analytics Data API enabled
   - A service account with appropriate permissions

## Step 1: Enable Google Analytics APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Enable the following APIs:
   - [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
   - [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

## Step 2: Create a Service Account

1. In the Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Enter a name (e.g., "analytics-mcp-cloudflare") and click **Create**
4. Click **Continue** (no need to grant specific roles at project level)
5. Click **Done**

## Step 3: Grant Service Account Access to Google Analytics

1. Go to [Google Analytics](https://analytics.google.com/)
2. Navigate to **Admin** (bottom left)
3. Select your **Account** and/or **Property**
4. Click **Account Access Management** or **Property Access Management**
5. Click the **+** button and select **Add users**
6. Enter your service account email (looks like `name@project-id.iam.gserviceaccount.com`)
7. Select **Viewer** role (read-only access)
8. Click **Add**

## Step 4: Create Service Account Key

1. In Google Cloud Console, go back to **IAM & Admin** > **Service Accounts**
2. Click on your service account
3. Go to the **Keys** tab
4. Click **Add Key** > **Create new key**
5. Select **JSON** format
6. Click **Create** - this will download a JSON file
7. **Important**: Keep this file secure and never commit it to version control

## Step 5: Install Wrangler CLI

Install Cloudflare's Wrangler CLI tool:

```bash
npm install -g wrangler
```

Login to your Cloudflare account:

```bash
wrangler login
```

## Step 6: Create KV Namespace

Create a KV namespace for storing authentication tokens and state:

```bash
# Create production namespace
wrangler kv:namespace create "MCP_STATE"

# Create preview namespace for development
wrangler kv:namespace create "MCP_STATE" --preview
```

You'll receive output like:

```
{ binding = "MCP_STATE", id = "abc123..." }
{ binding = "MCP_STATE", preview_id = "xyz789..." }
```

## Step 7: Configure wrangler.toml

1. Open `wrangler.toml` in the `cloudflare/` directory
2. Update the KV namespace IDs with the values from Step 6:

```toml
[[kv_namespaces]]
binding = "MCP_STATE"
id = "abc123..."  # Replace with your production ID
preview_id = "xyz789..."  # Replace with your preview ID
```

3. Optionally, set public environment variables:

```toml
[vars]
GOOGLE_CLOUD_PROJECT = "your-project-id"
```

## Step 8: Set Environment Secrets

Set your service account credentials as a secret (this keeps them encrypted):

```bash
cd cloudflare/

# Set the service account key as a secret
# Copy the entire contents of your downloaded JSON key file
wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY
# When prompted, paste the entire JSON content and press Enter, then Ctrl+D
```

The JSON should look like:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "name@project-id.iam.gserviceaccount.com",
  ...
}
```

## Step 9: Install Dependencies

```bash
cd cloudflare/
npm install
```

## Step 10: Deploy to Cloudflare Workers

Deploy your MCP server:

```bash
npm run deploy
```

After successful deployment, you'll see:

```
Published analytics-mcp (X.XX sec)
  https://analytics-mcp.your-subdomain.workers.dev
```

Save this URL - you'll need it to connect your MCP client.

## Step 11: Test Your Deployment

You can test your deployment with a simple curl command:

```bash
curl -X POST https://analytics-mcp.your-subdomain.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

You should receive a JSON response with server information.

## Step 12: Configure Your MCP Client

To use this server with an MCP client (like Claude Desktop or Gemini CLI), configure it to connect to your Cloudflare Worker URL.

### For Gemini CLI / Gemini Code Assist

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "analytics-mcp-cloudflare": {
      "url": "https://analytics-mcp.your-subdomain.workers.dev",
      "transport": "http"
    }
  }
}
```

### For Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "analytics-mcp-cloudflare": {
      "url": "https://analytics-mcp.your-subdomain.workers.dev",
      "transport": "http"
    }
  }
}
```

## Using Persistent Storage

The MCP server uses Cloudflare KV to cache authentication tokens. This provides:

- **Automatic token refresh**: Tokens are cached and automatically refreshed when expired
- **Fast authentication**: Subsequent requests use cached tokens for better performance
- **Stateful sessions**: You can store additional state information if needed

To access stored state from your worker code:

```typescript
// Store data
await env.MCP_STATE.put('my-key', 'my-value');

// Retrieve data
const value = await env.MCP_STATE.get('my-key');

// Store with expiration (in seconds)
await env.MCP_STATE.put('my-key', 'my-value', { expirationTtl: 3600 });
```

## Available MCP Tools

Once connected, you can use the following tools:

1. **get_account_summaries** - Get all Google Analytics accounts and properties
2. **get_property_details** - Get details about a specific property
3. **list_google_ads_links** - List Google Ads links for a property
4. **run_report** - Run a Google Analytics report
5. **run_realtime_report** - Run a realtime report
6. **get_custom_dimensions_and_metrics** - Get custom dimensions and metrics

### Example Prompts

- "Show me all my Google Analytics properties"
- "What are the top pages on my website in the last 30 days?"
- "How many active users do I have right now?"
- "What custom dimensions are configured in my property?"

## Troubleshooting

### Authentication Errors

If you see authentication errors:

1. Verify your service account has access to your Google Analytics property
2. Check that the JSON key is correctly formatted (no extra spaces or line breaks)
3. Ensure the Google Analytics APIs are enabled in your project

### Token Expiration

Tokens are automatically cached and refreshed. If you see token-related errors:

1. Clear the KV namespace: `wrangler kv:key delete --namespace-id=YOUR_ID "google_access_token"`
2. Verify your service account key is valid

### Deployment Issues

If deployment fails:

1. Ensure you're logged in: `wrangler whoami`
2. Check your `wrangler.toml` configuration
3. Verify your KV namespace IDs are correct

### API Quota Limits

Google Analytics APIs have quota limits. If you hit these limits:

1. Check your quota usage in Google Cloud Console
2. Request a quota increase if needed
3. Implement caching in your application to reduce API calls

## Local Development

To test locally before deploying:

```bash
cd cloudflare/
npm run dev
```

This starts a local server at `http://localhost:8787`. You can test it with the same curl commands, replacing the URL with `http://localhost:8787`.

## Security Best Practices

1. **Never commit secrets**: Keep your service account JSON file secure and never commit it to version control
2. **Use secrets for credentials**: Always use `wrangler secret put` for sensitive data
3. **Limit service account permissions**: Grant only necessary permissions (Viewer role for read-only access)
4. **Monitor usage**: Regularly check your Cloudflare Workers analytics dashboard
5. **Rotate keys**: Periodically rotate your service account keys

## Cost Considerations

Cloudflare Workers Free Tier includes:

- 100,000 requests per day
- 10ms CPU time per request

For most use cases, this is sufficient. If you exceed these limits, Cloudflare Workers Paid plan is $5/month for 10 million requests.

KV storage costs:

- First 1 GB: Free
- Read operations: $0.50 per million reads
- Write operations: $5.00 per million writes

## Support and Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Google Analytics API Documentation](https://developers.google.com/analytics)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

## Updating the Worker

To update your worker after making changes:

```bash
cd cloudflare/
npm run deploy
```

Changes take effect immediately after deployment.

## Removing the Worker

To remove the worker and clean up resources:

```bash
cd cloudflare/
wrangler delete analytics-mcp
```

To delete KV namespaces:

```bash
wrangler kv:namespace delete --namespace-id=YOUR_NAMESPACE_ID
```

## Frequently Asked Questions (FAQ)

### Q: Do I need a Cloudflare Workers paid plan?

A: No! The free tier includes 100,000 requests per day, which is sufficient for most use cases. You only need the paid plan ($5/month) if you exceed this limit.

### Q: Can I use this with my existing Google Analytics user credentials?

A: **For Cloudflare Workers deployment:** No, you must use a service account. Service accounts are designed for server-to-server authentication and are more secure for production deployments.

**For local Python server:** Yes! The local server now supports OAuth 2.0 user authentication. See the [OAuth Setup Guide](../docs/OAUTH_SETUP.md) for instructions. You can authenticate with your Google account instead of using service accounts or ADC.

### Q: How much does Cloudflare KV storage cost?

A: The first 1 GB is free. Read operations cost $0.50 per million reads, and writes cost $5 per million writes. For typical MCP usage (mainly token caching), costs are negligible.

### Q: Can I use multiple Google Analytics properties?

A: Yes! The service account just needs to be granted access to all the properties you want to query. Add the service account email to each property's access management.

### Q: How do I update my service account credentials?

A: Use `wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY` to update the secret. Changes take effect immediately.

### Q: What regions does this deploy to?

A: Cloudflare Workers deploy to Cloudflare's entire global network automatically. Your code runs on the edge closest to your users.

### Q: How do I see logs and debug issues?

A: Use `wrangler tail` to see real-time logs from your worker. You can also view logs in the Cloudflare dashboard.

### Q: Can I use this with the Python MCP server?

A: Yes! You can run both the Python server locally and the Cloudflare Worker deployment. They're independent and use different authentication methods:
- **Local Python server**: Supports OAuth 2.0 (user authentication) OR Application Default Credentials (ADC)
- **Cloudflare Workers**: Uses service account authentication only

See the main [README](../README.md) for local server setup with OAuth, or [OAUTH_SETUP.md](../docs/OAUTH_SETUP.md) for detailed OAuth instructions.

### Q: Is my service account key secure?

A: Yes. Cloudflare encrypts all secrets, and they're never exposed in logs or responses. Never commit the JSON key file to version control.

### Q: Can I restrict access to specific IP addresses?

A: Yes, you can add IP filtering in the worker code or use Cloudflare Access for more advanced access control.

### Q: What's the latency like?

A: Very low! Cloudflare Workers run on the edge close to users. The main latency comes from calling Google Analytics APIs, which is unavoidable.

### Q: Can I use custom domains?

A: Yes! You can configure a custom domain in the Cloudflare dashboard under Workers & Pages > your worker > Settings > Domains.

### Q: How do I monitor usage and costs?

A: Check the Cloudflare dashboard for request counts and Worker analytics. KV usage is shown under Workers & Pages > KV.
