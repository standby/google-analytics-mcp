# Google Analytics MCP Server for Cloudflare Workers

This directory contains a Cloudflare Workers implementation of the Google Analytics MCP Server, allowing you to run the server on Cloudflare's edge network.

## Features

- **Serverless deployment**: No infrastructure to manage
- **Global edge network**: Low latency from anywhere in the world
- **Automatic scaling**: Handles any traffic volume
- **Persistent storage**: Uses Cloudflare KV for caching tokens and state
- **Secure credentials**: Environment variables and secrets stored securely in Cloudflare dashboard
- **Cost-effective**: Free tier includes 100,000 requests/day

## Quick Start

See [CLOUDFLARE_SETUP.md](./CLOUDFLARE_SETUP.md) for detailed setup instructions.

### Prerequisites

- Node.js 18+
- Cloudflare account
- Google Cloud project with Analytics APIs enabled
- Service account with Analytics permissions

### Installation

```bash
cd cloudflare/
npm install
```

### Configuration

1. Create KV namespace:
   ```bash
   wrangler kv:namespace create "MCP_STATE"
   wrangler kv:namespace create "MCP_STATE" --preview
   ```

2. Update `wrangler.toml` with your KV namespace IDs

3. Set service account credentials:
   ```bash
   wrangler secret put GOOGLE_SERVICE_ACCOUNT_KEY
   ```

### Deploy

```bash
npm run deploy
```

### Local Development

```bash
npm run dev
```

## Architecture

- **index.ts**: Main entry point and request handler
- **auth.ts**: Google OAuth authentication and token management
- **analytics-client.ts**: Google Analytics API client
- **mcp-server.ts**: MCP protocol implementation and tool handlers

## Available Tools

1. `get_account_summaries` - List all Google Analytics accounts and properties
2. `get_property_details` - Get property details
3. `list_google_ads_links` - List Google Ads links
4. `run_report` - Run analytics reports
5. `run_realtime_report` - Run realtime reports
6. `get_custom_dimensions_and_metrics` - Get custom dimensions and metrics

## Storage

Uses Cloudflare KV for:
- OAuth token caching (automatic refresh)
- Session state
- User preferences

## Security

- Service account credentials stored as encrypted secrets
- Tokens cached with automatic expiration
- No credentials in code or configuration files
- CORS headers configured for security

## Documentation

- [Setup Guide](./CLOUDFLARE_SETUP.md) - Complete setup instructions
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Step-by-step deployment guide
- [Architecture Overview](./ARCHITECTURE.md) - Technical architecture and design
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Google Analytics API Docs](https://developers.google.com/analytics)

## Support

For issues specific to the Cloudflare implementation, please open an issue on the main repository.
