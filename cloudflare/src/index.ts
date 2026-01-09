/**
 * Copyright 2025 Google LLC All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Google Analytics MCP Server for Cloudflare Workers
 */

import { getAccessToken } from './auth';
import { AnalyticsClient } from './analytics-client';
import { createMCPServer } from './mcp-server';

interface Env {
  MCP_STATE: KVNamespace;
  GOOGLE_SERVICE_ACCOUNT_KEY: string;
  GOOGLE_CLOUD_PROJECT?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      // Parse the MCP request
      const mcpRequest = await request.json();

      // Get access token
      const accessToken = await getAccessToken(env, env.MCP_STATE);

      // Create Analytics client
      const analyticsClient = new AnalyticsClient(accessToken);

      // Create MCP server handler
      const mcpServer = createMCPServer(analyticsClient, env.MCP_STATE);

      // Handle the request
      const response = await mcpServer.handleRequest(mcpRequest);

      // Return response
      return new Response(JSON.stringify(response), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    } catch (error: any) {
      console.error('Error handling request:', error);
      return new Response(
        JSON.stringify({
          error: {
            code: -32603,
            message: error.message || 'Internal server error',
          },
        }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
        }
      );
    }
  },

  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    // Optional: Implement scheduled token refresh or cleanup
    console.log('Scheduled event triggered');
  },
};
