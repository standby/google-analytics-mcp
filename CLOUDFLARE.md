# Cloudflare Workers Deployment

The Google Analytics MCP Server can now be deployed to [Cloudflare Workers](https://workers.cloudflare.com/), enabling serverless, globally distributed deployment.

## Why Cloudflare Workers?

- ✅ **Serverless**: No infrastructure to manage
- ✅ **Global**: Runs on Cloudflare's edge network in 300+ cities
- ✅ **Scalable**: Automatically handles any traffic volume
- ✅ **Fast**: Low latency worldwide with edge computing
- ✅ **Affordable**: Free tier includes 100,000 requests/day
- ✅ **Secure**: Encrypted secrets, HTTPS only
- ✅ **Simple**: Deploy in minutes with Wrangler CLI

## Quick Start

### Prerequisites

1. [Cloudflare account](https://dash.cloudflare.com/sign-up) (free tier works)
2. [Node.js](https://nodejs.org/) 18+ installed
3. Google Cloud project with Analytics APIs enabled
4. Service account with Analytics access

### Deploy in 5 Steps

```bash
# 1. Install Wrangler CLI
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Create KV namespace for state storage
cd cloudflare/
wrangler kv:namespace create "MCP_STATE"
wrangler kv:namespace create "MCP_STATE" --preview

# 4. Configure wrangler.toml with namespace IDs
# Edit cloudflare/wrangler.toml and update the KV namespace IDs

# 5. Set service account credentials and deploy
wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY
# Paste your service account JSON when prompted
npm install
npm run deploy
```

Your MCP server is now live at `https://analytics-mcp.your-subdomain.workers.dev`!

## Documentation

📚 **[Complete Setup Guide](cloudflare/CLOUDFLARE_SETUP.md)** - Step-by-step instructions

📋 **[Deployment Checklist](cloudflare/DEPLOYMENT_CHECKLIST.md)** - Verification checklist

🏗️ **[Architecture Overview](cloudflare/ARCHITECTURE.md)** - Technical design details

❓ **[FAQ](cloudflare/CLOUDFLARE_SETUP.md#frequently-asked-questions-faq)** - Common questions

## Features

### All MCP Tools Supported

The Cloudflare deployment includes all tools from the Python version:

- `get_account_summaries` - List accounts and properties
- `get_property_details` - Get property details
- `list_google_ads_links` - List Google Ads links
- `run_report` - Run historical reports
- `run_realtime_report` - Run realtime reports  
- `get_custom_dimensions_and_metrics` - Get custom definitions

### Persistent Storage

Uses Cloudflare KV for:
- OAuth token caching (automatic refresh)
- Session state management
- Custom data storage

### Security

- Service account credentials stored as encrypted secrets
- Tokens never exposed to clients
- HTTPS only, CORS configured
- Read-only Analytics access

## Connecting MCP Clients

### Gemini CLI / Code Assist

Edit `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "analytics-mcp-cloudflare": {
      "url": "https://your-worker.workers.dev",
      "transport": "http"
    }
  }
}
```

### Claude Desktop

Edit your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "analytics-mcp-cloudflare": {
      "url": "https://your-worker.workers.dev",
      "transport": "http"
    }
  }
}
```

## Local Development

Test locally before deploying:

```bash
cd cloudflare/
npm run dev
```

Server runs at `http://localhost:8787`

Test with:

```bash
./test-requests.sh http://localhost:8787
```

## Cost Estimate

### Typical Usage (Light - 1,000 requests/day)

| Service | Usage | Cost |
|---------|-------|------|
| Cloudflare Workers | 30K requests/month | **Free** |
| KV Storage | 30K reads, 100 writes | **Free** |
| **Total** | | **$0/month** |

### Heavy Usage (100,000 requests/day)

| Service | Usage | Cost |
|---------|-------|------|
| Cloudflare Workers | 3M requests/month | **Free** |
| KV Storage | 3M reads, 3K writes | **~$1.50/month** |
| **Total** | | **~$1.50/month** |

### Enterprise (1M requests/day)

| Service | Usage | Cost |
|---------|-------|------|
| Cloudflare Workers | 30M requests/month | **$5/month** (Workers Paid) |
| KV Storage | 30M reads, 30K writes | **~$15/month** |
| **Total** | | **~$20/month** |

## Comparison: Local vs. Cloudflare

| Feature | Local Python | Cloudflare Workers |
|---------|--------------|-------------------|
| **Infrastructure** | User's machine | Cloudflare edge |
| **Scalability** | Limited by machine | Unlimited |
| **Availability** | When computer on | 24/7 global |
| **Latency** | Local only | Low worldwide |
| **Setup** | Python, pipx, ADC | Node, Wrangler |
| **Cost** | Free | Free - $5/month |
| **Credentials** | ADC file | Service account |
| **Best For** | Desktop apps | Cloud/production |

## Troubleshooting

### Common Issues

**Authentication Error**
- Verify service account JSON is valid
- Check service account has Analytics access
- Ensure APIs are enabled in Google Cloud

**KV Namespace Error**  
- Verify namespace IDs in wrangler.toml
- Check namespaces exist: `wrangler kv:namespace list`

**Deployment Fails**
- Login to Cloudflare: `wrangler whoami`
- Check wrangler.toml syntax
- Verify npm dependencies installed

**See Detailed Logs**
```bash
wrangler tail
```

## Updating

After code changes:

```bash
cd cloudflare/
npm run deploy
```

Changes go live immediately (no restart needed).

To update credentials:

```bash
wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY
```

## Support

- 📖 [Full Documentation](cloudflare/)
- 💬 [Discord Channel](https://discord.com/channels/971845904002871346/1398002598665257060)
- 🐛 [Report Issues](https://github.com/googleanalytics/google-analytics-mcp/issues)

## Next Steps

1. Follow the [Complete Setup Guide](cloudflare/CLOUDFLARE_SETUP.md)
2. Test locally with `npm run dev`
3. Deploy to production
4. Connect your MCP client
5. Start querying Google Analytics!

---

**Note**: Both the local Python server and Cloudflare deployment can coexist. Use the local server for desktop applications and Cloudflare for production/cloud integrations.
