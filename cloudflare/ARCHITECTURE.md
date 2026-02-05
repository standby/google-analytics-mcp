# Architecture Overview

This document describes the architecture of the Google Analytics MCP Server on Cloudflare Workers.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Client                              │
│           (Claude Desktop, Gemini CLI, etc.)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/JSON-RPC
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   Cloudflare Workers                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  index.ts (Entry Point)                   │ │
│  │  • CORS Handling                                          │ │
│  │  • Request Routing                                        │ │
│  │  • Error Handling                                         │ │
│  └─────────────┬──────────────────┬──────────────────────────┘ │
│                │                  │                             │
│  ┌─────────────▼───────┐  ┌──────▼──────────────────────────┐ │
│  │     auth.ts         │  │    mcp-server.ts                │ │
│  │  • JWT Creation     │  │  • MCP Protocol Handler         │ │
│  │  • Token Exchange   │  │  • Tool Registration            │ │
│  │  • Token Caching    │  │  • Request/Response Formatting  │ │
│  └─────────┬───────────┘  └────────┬────────────────────────┘ │
│            │                       │                            │
│            │         ┌─────────────▼──────────────────┐        │
│            │         │    analytics-client.ts         │        │
│            │         │  • API Abstraction             │        │
│            │         │  • Request Construction        │        │
│            │         │  • Response Parsing            │        │
│            │         └─────────────┬──────────────────┘        │
│            │                       │                            │
└────────────┼───────────────────────┼────────────────────────────┘
             │                       │
             │                       │
    ┌────────▼───────┐      ┌───────▼─────────────────────┐
    │  Cloudflare KV │      │  Google Analytics APIs      │
    │                │      │  • Admin API (v1beta)       │
    │  • Token Cache │      │  • Data API (v1beta)        │
    │  • State Store │      │  • REST/JSON                │
    └────────────────┘      └─────────────────────────────┘
```

## Component Details

### 1. index.ts (Entry Point)

**Responsibilities:**
- Receives HTTP requests from MCP clients
- Handles CORS preflight (OPTIONS) requests
- Orchestrates authentication and request handling
- Returns formatted responses
- Manages global error handling

**Flow:**
1. Check if request is OPTIONS (CORS preflight) → return early
2. Parse JSON-RPC request body
3. Get access token (may trigger token refresh)
4. Create Analytics API client
5. Create MCP server handler
6. Process request and return response

### 2. auth.ts (Authentication)

**Responsibilities:**
- Manage Google service account authentication using OAuth 2.0 protocol
- Create and sign JWTs using RS256 algorithm
- Exchange JWTs for access tokens
- Cache tokens in KV storage
- Automatically refresh expired tokens

> **Note:** This uses service account authentication (server-to-server), not user OAuth. For user OAuth authentication, see the [local Python server](../docs/OAUTH_SETUP.md).

**Key Functions:**
- `getAccessToken()`: Main entry point, checks cache first
- `createJWT()`: Creates a signed JWT for service account
- `signJWT()`: Uses Web Crypto API to sign with RSA-SHA256

**Token Lifecycle:**
```
1. Check KV cache → Token valid? → Return cached token
                  ↓ No
2. Create JWT with service account key
                  ↓
3. Exchange JWT for access token at token_uri
                  ↓
4. Cache token in KV with expiration (3600s - 60s buffer)
                  ↓
5. Return access token
```

### 3. mcp-server.ts (MCP Protocol Handler)

**Responsibilities:**
- Implement MCP JSON-RPC protocol
- Register and describe available tools
- Route tool calls to appropriate handlers
- Format responses according to MCP spec

**Supported Methods:**
- `initialize`: Returns server capabilities
- `tools/list`: Returns list of available tools
- `tools/call`: Executes a specific tool

**Available Tools:**
1. `get_account_summaries` - List accounts and properties
2. `get_property_details` - Get property details
3. `list_google_ads_links` - List Google Ads links
4. `run_report` - Run historical reports
5. `run_realtime_report` - Run realtime reports
6. `get_custom_dimensions_and_metrics` - Get custom definitions

### 4. analytics-client.ts (API Client)

**Responsibilities:**
- Abstract Google Analytics REST APIs
- Construct API request URLs
- Make authenticated HTTP requests
- Parse and return API responses
- Handle API errors

**API Endpoints Used:**
- Admin API: `https://analyticsadmin.googleapis.com/v1beta/...`
- Data API: `https://analyticsdata.googleapis.com/v1beta/...`

## Data Flow Example

### Example: get_account_summaries Tool Call

```
1. Client → Worker
   POST /
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "get_account_summaries",
       "arguments": {}
     }
   }

2. Worker: Check token cache
   - Check KV: google_access_token
   - If expired or missing → Generate new token

3. Worker: Generate JWT (if needed)
   - Header: {"alg": "RS256", "typ": "JWT"}
   - Payload: {iss, scope, aud, exp, iat}
   - Sign with service account private key

4. Worker: Exchange JWT for token (if needed)
   - POST to token_uri
   - Receive access_token and expires_in
   - Cache in KV

5. Worker: Call Google Analytics API
   - GET https://analyticsadmin.googleapis.com/v1beta/accountSummaries
   - Authorization: Bearer {access_token}

6. Worker → Client: Return results
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "content": [{
         "type": "text",
         "text": "[{...accounts...}]"
       }]
     }
   }
```

## Security Architecture

### Secrets Management
- Service account keys stored as encrypted Cloudflare secrets
- Never exposed in logs, code, or responses
- Accessed via `env.GOOGLE_SERVICE_ACCOUNT_KEY`

### Token Security
- Access tokens cached in KV (not exposed to clients)
- Automatic expiration and refresh
- 60-second buffer to prevent using near-expired tokens

### Network Security
- HTTPS only (enforced by Cloudflare)
- CORS headers properly configured
- No client-side credentials required

### API Security
- Read-only scope: `analytics.readonly`
- Service account principle of least privilege
- Property-level access control via GA permissions

## Performance Optimizations

### Token Caching
- Tokens valid for 3600 seconds
- Cached in KV to avoid repeated auth calls
- Significant latency reduction (no auth on cache hit)

### Edge Computing
- Code runs on Cloudflare's edge network
- Low latency to clients worldwide
- Automatic scaling

### Efficient API Calls
- Direct REST API calls (no heavy SDK dependencies)
- Minimal parsing and transformation
- Parallel processing where possible

## Scalability

### Cloudflare Workers
- Automatically scales to handle any traffic
- No configuration needed
- Isolated execution per request

### Rate Limits
**Cloudflare:**
- Free: 100,000 requests/day
- Paid: 10M requests/month ($5)

**Google Analytics APIs:**
- Check quotas in Google Cloud Console
- Implement client-side caching if needed

### Storage (KV)
- First 1 GB free
- Unlimited namespace size
- Global replication

## Monitoring and Debugging

### Available Tools
- `wrangler tail`: Real-time log streaming
- Cloudflare Dashboard: Analytics and metrics
- `console.log()`: Appears in wrangler tail

### Key Metrics
- Request count
- Error rate
- CPU time per request
- KV operations

### Common Issues
1. **Authentication errors**: Check service account key format
2. **API quota exceeded**: Monitor Google Cloud Console
3. **Token cache issues**: Clear KV and retry
4. **CORS errors**: Verify preflight handling

## Deployment

### Build Process
- TypeScript compiled by Wrangler at deploy time
- No separate build step needed
- Source maps not included (production)

### Deployment Pipeline
```
Local → wrangler deploy → Cloudflare Edge
  ↓                          ↓
  TypeScript               JavaScript
  + Config                 + Runtime
```

### Zero-Downtime Updates
- New code uploaded
- Tested on edge
- Rolled out globally
- No downtime

## Future Enhancements

Potential improvements:
1. **Response caching**: Cache GA API responses in KV
2. **Batch operations**: Support multiple tool calls in one request
3. **Webhooks**: Support for async operations
4. **Custom domains**: Use organization domain
5. **Rate limiting**: Implement per-client rate limits
6. **Metrics**: Custom analytics for usage tracking
