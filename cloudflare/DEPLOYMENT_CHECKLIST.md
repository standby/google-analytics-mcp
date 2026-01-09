# Cloudflare Deployment Checklist

Use this checklist to ensure you've completed all steps for deploying the Google Analytics MCP Server to Cloudflare Workers.

## Pre-deployment Setup

- [ ] **Google Cloud Project**
  - [ ] Created a Google Cloud project
  - [ ] Enabled Google Analytics Admin API
  - [ ] Enabled Google Analytics Data API

- [ ] **Service Account**
  - [ ] Created a service account in Google Cloud
  - [ ] Downloaded the service account JSON key file
  - [ ] Granted the service account access to Google Analytics properties (Viewer role)

- [ ] **Local Environment**
  - [ ] Installed Node.js (v18+)
  - [ ] Installed Wrangler CLI: `npm install -g wrangler`
  - [ ] Logged in to Cloudflare: `wrangler login`

## Cloudflare Configuration

- [ ] **KV Namespace**
  - [ ] Created production KV namespace: `wrangler kv:namespace create "MCP_STATE"`
  - [ ] Created preview KV namespace: `wrangler kv:namespace create "MCP_STATE" --preview`
  - [ ] Copied the namespace IDs from the output

- [ ] **wrangler.toml**
  - [ ] Updated `id` with production KV namespace ID
  - [ ] Updated `preview_id` with preview KV namespace ID
  - [ ] (Optional) Set GOOGLE_CLOUD_PROJECT in `[vars]` section

- [ ] **Secrets**
  - [ ] Set GOOGLE_SERVICE_ACCOUNT_KEY: `wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY`
  - [ ] Pasted entire JSON key file content when prompted

## Deployment

- [ ] **Install Dependencies**
  - [ ] Ran `npm install` in the `cloudflare/` directory

- [ ] **Deploy**
  - [ ] Ran `npm run deploy`
  - [ ] Noted the deployed worker URL
  - [ ] Verified deployment was successful

## Testing

- [ ] **Test Initialize**
  ```bash
  curl -X POST https://your-worker.workers.dev \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}'
  ```
  - [ ] Received successful response

- [ ] **Test Tools List**
  ```bash
  curl -X POST https://your-worker.workers.dev \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
  ```
  - [ ] Received list of 6 tools

## MCP Client Configuration

- [ ] **Gemini CLI / Code Assist**
  - [ ] Updated `~/.gemini/settings.json` with worker URL
  - [ ] Restarted Gemini CLI/Code Assist

- [ ] **Claude Desktop** (if applicable)
  - [ ] Updated Claude Desktop config with worker URL
  - [ ] Restarted Claude Desktop

- [ ] **Test with Client**
  - [ ] Verified server shows up in MCP server list
  - [ ] Successfully ran a test query (e.g., "Show my Google Analytics properties")

## Post-deployment

- [ ] **Documentation**
  - [ ] Saved the worker URL for future reference
  - [ ] Documented any custom configuration
  - [ ] Shared setup with team members (if applicable)

- [ ] **Monitoring**
  - [ ] Bookmarked Cloudflare Workers dashboard for your worker
  - [ ] Checked initial logs for any errors

- [ ] **Security**
  - [ ] Verified service account JSON file is NOT in version control
  - [ ] Verified secrets are stored securely
  - [ ] Considered setting up additional access controls if needed

## Troubleshooting

If something isn't working:

1. Check Cloudflare Workers logs: `wrangler tail`
2. Verify secrets are set: `wrangler secret list`
3. Test authentication with curl commands above
4. Check Google Analytics API quotas in Google Cloud Console
5. Verify service account has access to GA properties

## Notes

- Free tier: 100,000 requests/day
- KV storage: First 1 GB free
- Deployment takes ~30 seconds
- Changes are live immediately after deployment
- No need to restart anything after updates

## Update Procedure

To update the worker after code changes:

1. Make your changes in `src/`
2. Run `npm run deploy`
3. Changes go live immediately

To update secrets:

1. Run `wrangler secret put SECRET_NAME`
2. Enter new value
3. Changes take effect immediately
